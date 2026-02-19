# mkdir build
rm .\build\Debug\bookapp.exe
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=P:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build .
cd ..
.\build\Debug\bookapp.exe
