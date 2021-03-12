sudo apt-get install git cmake build-essential libboost-all-dev libprotobuf17 protobuf-compiler libprotobuf-dev openssl libssl-dev libgoogle-perftools-dev

git clone https://github.com/marian-nmt/marian-dev.git

cd marian-dev

mkdir build

cd build

cmake .. -DUSE_STATIC_LIBS=on -DCOMPILE_SERVER=on

make -j4
