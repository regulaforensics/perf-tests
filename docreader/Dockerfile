# FROM regulaforensics/docreader:7.4 AS builder_74

FROM regulaforensics/docreader:7.5

RUN rm -f /app/extBin/unix/libProcMgr.so && ls -lah /app/extBin/unix

#COPY --chown=1001:0 ./runner_gunicorn.py /app/src/runner_gunicorn.py
COPY --chown=1001:0 ./libProcMgr.so /app/extBin/unix

