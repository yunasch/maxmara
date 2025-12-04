# ==============================
# STAGE 1: Builder
# ==============================
ARG ODOO_VERSION=reg.bdr.group/o-img:18.0e
FROM ${ODOO_VERSION} AS builder

ARG ODOO_VERSION=reg.bdr.group/o-img:18.0e
ARG BRANCH
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]
USER root

# Set environment variables
ENV ODOO_VERSION=${ODOO_VERSION} \
    BRANCH=${BRANCH} \
    MAIN_BRANCH=18.0
#    SSH_DIR=/root/.ssh \
#    BASE_DIR=/mnt/extra-addons/BDR

# Copy odoo.conf
COPY odoo.conf /mnt/odoo.conf
COPY staging-odoo.conf /mnt/staging-odoo.conf
RUN if [ "$BRANCH" = "$MAIN_BRANCH" ]; then \
    rm /mnt/staging-odoo.conf; \
    else \
    mv /mnt/staging-odoo.conf /mnt/odoo.conf; \
    fi

# Copy custom modules from repo
COPY BDR/custom /mnt/extra-addons/BDR/custom

# ==============================
# STAGE 2: Final Image
# ==============================
FROM ${ODOO_VERSION} AS final
USER root

# Copy only necessary files
COPY --from=builder /mnt/extra-addons /mnt/extra-addons
COPY --from=builder /mnt/odoo.conf /mnt/odoo.conf

## Install requirements
#RUN find /mnt/extra-addons/OCA -type f -name "requirements.txt" -exec pip3 install -r {} \;
RUN pip3 install --break-system-packages pandas xlrd==2.0.1 openpyxl

RUN chown -R odoo:odoo /mnt/extra-addons /mnt/odoo.conf
RUN chmod -R 755 /mnt/extra-addons /mnt/odoo.conf

USER odoo
CMD ["odoo"]
