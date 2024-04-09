#!/bin//bash

cmake -DCMAKE_CXX_COMPIELR=clang++ -DCMAKE_C_COMPILER=clang . && \
make -j && \
cd vite-baseball-stats && \
npm install && \
npm run build