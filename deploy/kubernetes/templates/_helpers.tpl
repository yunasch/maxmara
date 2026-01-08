{{- define "odoo.name" -}}
{{- default "odoo" .Values.odoo.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "odoo.fullname" -}}
{{- if .Values.odoo.fullnameOverride -}}
{{- .Values.odoo.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "odoo.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}