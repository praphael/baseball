#!/bin//bash

cmake -DCMAKE_CXX_COMPIELR=clang++ -DCMAKE_C_COMPILER=clang . && \
make -j && \
cd vite-baseball-stats && \
cd src && \
sed 's/*console.log*/d/' $(find . -name '*.js*') && \
cd .. && \
npm install && \
npm run build