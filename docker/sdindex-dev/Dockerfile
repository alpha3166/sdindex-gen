FROM python
ARG USERNAME=me
RUN groupadd --gid 1000 $USERNAME && \
    useradd --uid 1000 --gid $USERNAME --create-home --shell /bin/bash $USERNAME
RUN apt update && \
    apt install --yes sudo && \
    echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME
RUN apt install --yes git less
RUN pip install --upgrade pip && \
    pip install autopep8 && \
    pip install beautifulsoup4
USER $USERNAME
