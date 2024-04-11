// Copyright (c) 2016-2019 Vinnie Falco (vinnie dot falco at gmail dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//
// Official repository: https://github.com/boostorg/beast
//

//------------------------------------------------------------------------------
//
// Example: HTTP server, asynchronous
//
//------------------------------------------------------------------------------

#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/dispatch.hpp>
#include <boost/asio/strand.hpp>
#include <boost/config.hpp>
#include <algorithm>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include <curl/curl.h>

#include "db.h"


using std::string;
using std::vector;
using std::unordered_map;
using std::cout;
using std::cerr;
using std::endl;

//const std::vector<string> API_ROOT = {"baseball", "api"};

namespace beast = boost::beast;         // from <boost/beast.hpp>
namespace http = beast::http;           // from <boost/beast/http.hpp>
namespace net = boost::asio;            // from <boost/asio.hpp>
using tcp = boost::asio::ip::tcp;       // from <boost/asio/ip/tcp.hpp>

// sqlite3* pdb;

// Return a reasonable mime type based on the extension of a file.
beast::string_view
mime_type(beast::string_view path)
{
    using beast::iequals;
    auto const ext = [&path]
    {
        auto const pos = path.rfind(".");
        if(pos == beast::string_view::npos)
            return beast::string_view{};
        return path.substr(pos);
    }();
    if(iequals(ext, ".htm"))  return "text/html";
    if(iequals(ext, ".html")) return "text/html";
    if(iequals(ext, ".php"))  return "text/html";
    if(iequals(ext, ".css"))  return "text/css";
    if(iequals(ext, ".txt"))  return "text/plain";
    if(iequals(ext, ".js"))   return "application/javascript";
    if(iequals(ext, ".json")) return "application/json";
    if(iequals(ext, ".xml"))  return "application/xml";
    if(iequals(ext, ".swf"))  return "application/x-shockwave-flash";
    if(iequals(ext, ".flv"))  return "video/x-flv";
    if(iequals(ext, ".png"))  return "image/png";
    if(iequals(ext, ".jpe"))  return "image/jpeg";
    if(iequals(ext, ".jpeg")) return "image/jpeg";
    if(iequals(ext, ".jpg"))  return "image/jpeg";
    if(iequals(ext, ".gif"))  return "image/gif";
    if(iequals(ext, ".bmp"))  return "image/bmp";
    if(iequals(ext, ".ico"))  return "image/vnd.microsoft.icon";
    if(iequals(ext, ".tiff")) return "image/tiff";
    if(iequals(ext, ".tif"))  return "image/tiff";
    if(iequals(ext, ".svg"))  return "image/svg+xml";
    if(iequals(ext, ".svgz")) return "image/svg+xml";
    return "application/text";
}

// Append an HTTP rel-path to a local filesystem path.
// The returned path is normalized for the platform.
std::string
path_cat(
    beast::string_view base,
    beast::string_view path)
{
    if(base.empty())
        return std::string(path);
    std::string result(base);
#ifdef BOOST_MSVC
    char constexpr path_separator = '\\';
    if(result.back() == path_separator)
        result.resize(result.size() - 1);
    result.append(path.data(), path.size());
    for(auto& c : result)
        if(c == '/')
            c = path_separator;
#else
    char constexpr path_separator = '/';
    if(result.back() == path_separator)
        result.resize(result.size() - 1);
    result.append(path.data(), path.size());
#endif
    return result;
}

// Return a response for the given request.
//
// The concrete type of the response message (which depends on the
// request), is type-erased in message_generator.
template <class Body, class Allocator>
http::message_generator
handle_request(
    beast::string_view doc_root,
    http::request<Body, http::basic_fields<Allocator>>&& req, 
    sqlite3* pdb)
{
    // Returns a bad request response
    auto const bad_request =
    [&req](beast::string_view why)
    {
        http::response<http::string_body> res{http::status::bad_request, req.version()};
        res.set(http::field::server, BOOST_BEAST_VERSION_STRING);
        res.set(http::field::content_type, "text/html");
        res.keep_alive(req.keep_alive());
        res.body() = std::string(why);
        res.prepare_payload();
        return res;
    };

    // Returns a not found response
    auto const not_found =
    [&req](beast::string_view target)
    {
        http::response<http::string_body> res{http::status::not_found, req.version()};
        res.set(http::field::server, BOOST_BEAST_VERSION_STRING);
        res.set(http::field::content_type, "text/html");
        res.keep_alive(req.keep_alive());
        res.body() = "The resource '" + std::string(target) + "' was not found.";
        res.prepare_payload();
        return res;
    };

    // Returns a server error response
    auto const server_error =
    [&req](beast::string_view what)
    {
        http::response<http::string_body> res{http::status::internal_server_error, req.version()};
        res.set(http::field::server, BOOST_BEAST_VERSION_STRING);
        res.set(http::field::content_type, "text/html");
        res.keep_alive(req.keep_alive());
        res.body() = "An error occurred: '" + std::string(what) + "'";
        res.prepare_payload();
        return res;
    };

    // Make sure we can handle the method
    if( req.method() != http::verb::get &&
        req.method() != http::verb::head && 
        req.method() != http::verb::options)
        return bad_request("Unknown HTTP-method");

    // Request path must be absolute and not contain "..".
    if( req.target().empty() ||
        req.target()[0] != '/' ||
        req.target().find("..") != beast::string_view::npos)
        return bad_request("Illegal request-target");

    auto tgt = string(req.target());
    int err = 0;
    CURL *curl = curl_easy_init();
    if(curl) {
        int decodelen;
        // char *decoded = curl_easy_unescape(curl, "%63%75%72%6c", 12, &decodelen);
        char *tgt_dec = curl_easy_unescape(curl, tgt.c_str(), tgt.size(), &decodelen);
        
        if(tgt_dec) {
            /* do not assume printf() works on the decoded data! */
            tgt = string(tgt_dec);
            cout << endl << "handleRequst tgt=" << tgt;
            curl_free(tgt_dec);
        } else {
            return bad_request("Could not parse query string");
        }
        curl_easy_cleanup(curl);
    } else {
        return bad_request("Could not initialize curl");
    } 

    auto paths = splitStr(tgt, '/');
    cout << endl << "handle_request: paths.size()= " << paths.size();
    cout << endl << "handle_request: paths= ";
    printVec(paths);
    if(paths.size() != 4)
        return not_found(req.target());
    if(paths[1] != "baseball" || paths[2] != "api")
        return not_found(req.target());
    // split into route/query string
    auto rt_qy = splitStr(paths[3], '?');
       
    string resp_body;
    auto mime_type = string("text/plain");
    static unordered_map<string, string> teamsMap;

    if (!err) {
        cout << endl << "rt_qy= ";
        printVec(rt_qy);
        string qy = "";
        auto rt = rt_qy[0];
        if (rt_qy.size() > 2)
            return bad_request("Bad query string");

        if (rt_qy.size() > 1)
            qy = rt_qy[1];
        try {
            if(rt == "parks") {
                if(req.method() == http::verb::get)
                    err = handleParksRequest(pdb, qy, resp_body, mime_type);
            }
            else if (rt == "teams") {
                if(req.method() == http::verb::get)
                    err = handleTeamsRequest(pdb, qy, resp_body, mime_type, teamsMap);
            }
            else if(rt == "box") {
                if(req.method() == http::verb::get)
                    err = handleBoxRequest(pdb, qy, resp_body, mime_type, teamsMap);
            } else {
                return not_found(req.target());
            }
        } catch (std::exception e) {
            std::cerr << endl << "exception during handle_request " << e.what();
            return server_error(e.what());
        }
    }
  
    // Cache the size since we need it after the move
    auto const size = resp_body.size();


    // Respond to HEAD request
    if(req.method() == http::verb::head || req.method() == http::verb::options)
    {
        http::response<http::empty_body> res{http::status::ok, req.version()};
        res.set(http::field::server, BOOST_BEAST_VERSION_STRING);
        res.set(http::field::content_type, mime_type);
        // CORS headers
        res.set("Access-Control-Allow-Origin", "*");
        res.set("Access-Control-Allow-Headers", "*");

        res.content_length(size);
        res.keep_alive(req.keep_alive());
        return res;
    }

    auto status = http::status::ok;
    if(err == 400)
        status = http::status::bad_request;
    if(err == 500)
        status = http::status::internal_server_error;

    // Respond to GET request
    http::response<http::string_body> res{
        std::piecewise_construct,
        std::make_tuple(std::move(resp_body)),
        std::make_tuple(status, req.version())};
    res.set(http::field::server, BOOST_BEAST_VERSION_STRING);
    res.set(http::field::content_type, mime_type);
    res.set("Access-Control-Allow-Origin", "*");
    res.content_length(size);
    res.keep_alive(req.keep_alive());

    return res;
}

//------------------------------------------------------------------------------

// Report a failure
void
fail(beast::error_code ec, char const* what)
{
    std::cerr << what << ": " << ec.message() << "\n";
}

// Handles an HTTP server connection
class session : public std::enable_shared_from_this<session>
{
    beast::tcp_stream stream_;
    beast::flat_buffer buffer_;
    std::shared_ptr<std::string const> doc_root_;
    http::request<http::string_body> req_;
    sqlite3 *pdb;

public:
    // Take ownership of the stream
    session(
        tcp::socket&& socket,
        std::shared_ptr<std::string const> const& doc_root,
        sqlite3 *pdb)
        : stream_(std::move(socket))
        , doc_root_(doc_root)
        , pdb(pdb)
    {
    }

    // Start the asynchronous operation
    void
    run()
    {
        // We need to be executing within a strand to perform async operations
        // on the I/O objects in this session. Although not strictly necessary
        // for single-threaded contexts, this example code is written to be
        // thread-safe by default.
        net::dispatch(stream_.get_executor(),
                      beast::bind_front_handler(
                          &session::do_read,
                          shared_from_this()));
    }

    void
    do_read()
    {
        // Make the request empty before reading,
        // otherwise the operation behavior is undefined.
        req_ = {};

        // Set the timeout.
        stream_.expires_after(std::chrono::seconds(3));

        // Read a request
        http::async_read(stream_, buffer_, req_,
            beast::bind_front_handler(
                &session::on_read,
                shared_from_this()));
    }

    void
    on_read(
        beast::error_code ec,
        std::size_t bytes_transferred)
    {
        boost::ignore_unused(bytes_transferred);

        // This means they closed the connection
        if(ec == http::error::end_of_stream)
            return do_close();

        if(ec)
            return fail(ec, "read");

        // Send the response
        send_response(
            handle_request(*doc_root_, std::move(req_), pdb));
    }

    void
    send_response(http::message_generator&& msg)
    {
        bool keep_alive = msg.keep_alive();

        // Write the response
        beast::async_write(
            stream_,
            std::move(msg),
            beast::bind_front_handler(
                &session::on_write, shared_from_this(), keep_alive));
    }

    void
    on_write(
        bool keep_alive,
        beast::error_code ec,
        std::size_t bytes_transferred)
    {
        boost::ignore_unused(bytes_transferred);

        if(ec)
            return fail(ec, "write");

        if(! keep_alive)
        {
            // This means we should close the connection, usually because
            // the response indicated the "Connection: close" semantic.
            return do_close();
        }

        // Read another request
        do_read();
    }

    void
    do_close()
    {
        // Send a TCP shutdown
        beast::error_code ec;
        stream_.socket().shutdown(tcp::socket::shutdown_send, ec);

        // At this point the connection is closed gracefully
    }
};

//------------------------------------------------------------------------------

// Accepts incoming connections and launches the sessions
class listener : public std::enable_shared_from_this<listener>
{
    net::io_context& ioc_;
    tcp::acceptor acceptor_;
    std::shared_ptr<std::string const> doc_root_;
    sqlite3 *pdb;

public:
    listener(
        net::io_context& ioc,
        tcp::endpoint endpoint,
        std::shared_ptr<std::string const> const& doc_root,
        int yearStart, 
        int yearEnd)
        : ioc_(ioc)
        , acceptor_(net::make_strand(ioc))
        , doc_root_(doc_root)
    {
        beast::error_code ec;
        initQueryParams();
        pdb = initDB(yearStart, yearEnd);

        // Open the acceptor
        acceptor_.open(endpoint.protocol(), ec);
        if(ec)
        {
            fail(ec, "open");
            return;
        }

        // Allow address reuse
        acceptor_.set_option(net::socket_base::reuse_address(true), ec);
        if(ec)
        {
            fail(ec, "set_option");
            return;
        }

        // Bind to the server address
        acceptor_.bind(endpoint, ec);
        if(ec)
        {
            fail(ec, "bind");
            return;
        }

        // Start listening for connections
        acceptor_.listen(
            net::socket_base::max_listen_connections, ec);
        if(ec)
        {
            fail(ec, "listen");
            return;
        }
    }

    // Start accepting incoming connections
    void
    run()
    {
        do_accept();
    }

private:
    void
    do_accept()
    {
        // The new connection gets its own strand
        acceptor_.async_accept(
            net::make_strand(ioc_),
            beast::bind_front_handler(
                &listener::on_accept,
                shared_from_this()));
    }

    void
    on_accept(beast::error_code ec, tcp::socket socket)
    {
        if(ec)
        {
            fail(ec, "accept");
            return; // To avoid infinite loop
        }
        else
        {
            // Create the session and run it
            std::make_shared<session>(
                std::move(socket),
                doc_root_, pdb)->run();
        }

        // Accept another connection
        do_accept();
    }
};


int main(int argc, char* argv[])
{
    // Check command line arguments.
    if (argc > 7)
    {
        std::cerr <<
            "Usage: httpd [<yearStart>] [<yearEnd>] [<address>] [<port>] [<doc_root>] [<threads>]\n" <<
            "Example:\n" <<
            "    httpd 1903 2022 0.0.0.0 8080 . 1\n";
        return EXIT_FAILURE;
    }
    // defaults
    auto yearStart = 1903;
    auto yearEnd = 2022;
    string address_str = "127.0.0.1";
    unsigned short port = 5000;
    string docroot = ".";
    int threads = 2;

    if (argc > 1)
        yearStart = std::atoi(argv[1]);
    if (argc > 2)
        yearEnd = std::atoi(argv[2]);
    if (argc > 3)
        address_str = string(argv[3]);
    if (argc > 4)
        port = static_cast<unsigned short>(std::atoi(argv[4]));
    if (argc > 5)
        docroot= string(argv[5]);
    if (argc > 6)
        threads = std::max<int>(1, std::atoi(argv[6]));

    auto doc_root = std::make_shared<string>(docroot);
    
    // The io_context is required for all I/O
    net::io_context ioc{threads};
    auto address = net::ip::make_address(address_str);
    std::cout << std::endl << "creating listening port";
    // Create and launch a listening port
    std::make_shared<listener>(
        ioc,
        tcp::endpoint{address, port},
        doc_root, yearStart, yearEnd)->run();


    std::cout << std::endl << "running io service";
    // Run the I/O service on the requested number of threads
    std::vector<std::thread> v;
    v.reserve(threads - 1);
    for(auto i = threads - 1; i > 0; --i)
        v.emplace_back(
        [&ioc]
        {
            ioc.run();
        });
    std::cout << std::endl << "invoking ioc.run()" << std::endl;
    ioc.run();

    return EXIT_SUCCESS;
}
