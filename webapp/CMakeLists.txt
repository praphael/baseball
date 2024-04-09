#
# Copyright (c) 2016-2017 Vinnie Falco (vinnie dot falco at gmail dot com)
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
# Official repository: https://github.com/boostorg/beast
#

cmake_minimum_required(VERSION 3.22)

project(httpd)
#GroupSources(include/boost/beast beast)
#GroupSources(example/http/server/async "/")

#find_package(boost)

find_package(CURL REQUIRED)

set(Boost_INCLUDE_DIRS "/usr/local/include")
#set(Boost_LIBRARY_DIRS "/boost_1_84_0/stage/lib")
include_directories(${Boost_INCLUDE_DIRS} ${CURL_INCLUDE_DIRS})
#link_directories(${Boost_LIBRARY_DIRS})


add_executable (httpd
    http.cpp
    sqlite3.c
    queries.cpp
    baseball_tables.cpp
    db.cpp
)

add_executable (test_qy
    test_queries.cpp
    queries.cpp
)

add_executable (test_db
    db.cpp
    sqlite3.c
    queries.cpp
    baseball_tables.cpp
    test_db.cpp
)

target_compile_features(httpd PRIVATE cxx_std_17)
target_compile_features(test_qy PRIVATE cxx_std_17)
target_compile_features(test_db PRIVATE cxx_std_17)

target_link_libraries(httpd
    ${CURL_LIBRARIES})
#target_link_libraries(httpd
#    lib-asio
#    lib-asio-ssl
#    lib-beast)

#set_property(TARGET http-server-async PROPERTY FOLDER "example-http-server")