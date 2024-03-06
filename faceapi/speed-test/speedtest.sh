#!/bin/sh
# These values can be overwritten with env variables

FACEAPI_HOST="${FACEAPI_HOST:-http://127.0.0.1:41101}"
SIZE_PACKAGE="${SIZE_PACKAGE:-10}"

run_speedtest()
{

    # Start speed test
    echo "Running a Speed Test..."
    file_size=$(stat -c%s "test.pdf")
    file_size=$(($file_size / 1024 / 1024))
    time_total=$(curl -o /dev/null -s -w '%{time_total}\n' --location "${FACEAPI_HOST}/api/v2/liveness?transactionId=000000-0000-0000-0000-000000000000" \
--header 'x-client-key: {"buffer":"121212121212","curveType":"prime256v1","keyType":"publicKey"}' \
--header 'Content-Type: application/octet-stream' \
--data '@test.pdf' )
    speed_limit=$(echo $file_size / $time_total | bc)
    max_network_rps=$(echo $speed_limit / ${SIZE_PACKAGE} | bc)
    echo "Local network speed is ${speed_limit} MB/s"
    echo "Max liveness rps limited network is ${max_network_rps} req/s"

}

run_speedtest

