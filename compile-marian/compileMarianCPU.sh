sudo apt-get install git cmake build-essential libboost-all-dev libprotobuf17 protobuf-compiler libprotobuf-dev openssl libssl-dev libgoogle-perftools-dev

wget -qO- 'https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB' | sudo apt-key add -

sudo sh -c 'echo deb https://apt.repos.intel.com/mkl all main > /etc/apt/sources.list.d/intel-mkl.list'

sudo apt-get update

sudo apt-get install intel-mkl-64bit-2020.0-088

git clone https://github.com/marian-nmt/marian-dev.git

cd marian-dev

mkdir -p buildCPU 

cd buildCPU

cmake .. -DUSE_STATIC_LIBS=on -DCOMPILE_SERVER=on -DCOMPILE_CPU=on -DCOMPILE_CUDA=off

make -j4

