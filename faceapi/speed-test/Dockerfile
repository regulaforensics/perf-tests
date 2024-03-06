FROM debian:bullseye

# Install basics
RUN apt-get update && apt-get install -y curl jq gnupg1 apt-transport-https dirmngr bc

# Download test file
RUN curl -o test.pdf https://files.testfile.org/PDF/100MB-TESTFILE.ORG.pdf

COPY ./speedtest.sh .
CMD ["./speedtest.sh"]
