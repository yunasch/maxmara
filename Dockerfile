ARG ODOO_VERSION=reg.bdr.group/o-img:17.0e
FROM ${ODOO_VERSION}
ARG ODOO_VERSION=reg.bdr.group/o-img:17.0e
ARG BRANCH
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]
USER root
CMD ["pkill -f odoo"]

ENV ODOO_VERSION=${ODOO_VERSION}
ENV BRANCH=${BRANCH}
ENV SSH_DIR=/root/.ssh
ENV BASE_DIR="BDR"

RUN if [ "$ODOO_VERSION" = "odoo:17" ]; then \
    apt-get update -y; \
    apt-get install -y git; \
    fi

RUN pip3 install pandas xlrd==2.0.1 openpyxl

RUN chown -R odoo:odoo /mnt/extra-addons
RUN chmod -R 755 /mnt/extra-addons

# Copy custom modules from repo
COPY maxmara_importation /mnt/extra-addons/maxmara_importation

# Copy odoo.conf
COPY odoo.conf /mnt/odoo.conf
COPY staging-odoo.conf /mnt/staging-odoo.conf
RUN if [ "$BRANCH" = "<main_branch>" ]; then \
    rm /mnt/staging-odoo.conf; \
    else \
    mv /mnt/staging-odoo.conf /mnt/odoo.conf; \
    fi

##Copy .git folder for recursive modules
#COPY .git /mnt/.git
#RUN ls -la /mnt/.git
#
#COPY .ssh/ /root/.ssh/
#RUN chmod 600 /root/.ssh/id_* && chmod 700 /root/.ssh

## Add Github to known host to avoid confirmation prompt and add the key(s) to the ssh-agent
#RUN ssh-keyscan github.com >> ${SSH_DIR}/known_hosts
#RUN eval "$(ssh-agent -s)" && \
#    for key in /root/.ssh/id_*; do \
#        ssh-add $key; \
#    done \
#    && ssh-add -l

## Set working directory
#WORKDIR /mnt/

## Dynamically update all submodules using their corresponding SSH keys only for private repos with ssh auth
#RUN for key in $SSH_DIR/id_*; do \
#    if [ -f "$key" ]; then \
#        REPO=$(basename "$key" | cut -d'_' -f2-); \
#        SUBMODULE_PATH="$BASE_DIR/$REPO"; \
#        echo "Updating submodule: $SUBMODULE_PATH using key: $key"; \
#        GIT_SSH_COMMAND="ssh -i $key -o StrictHostKeyChecking=no" git submodule update --init --recursive -- "$SUBMODULE_PATH"; \
#    fi; \
#done

## Update the rest of the submodules
#RUN git submodule update --init --recursive
#
## Delete .ssh folder
#RUN rm -rf /root/.ssh/ && rm -rf ../.ssh/*

## Install requirements
#RUN pip3 install -r /mnt/OCA/rest-framework/requirements.txt

USER odoo
CMD ["odoo"]