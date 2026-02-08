{{- /*
Expand the name of the chart.
*/}}
{{- define "ai-todo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- /*
Create a default fully qualified app name.
*/}}
{{- define "ai-todo.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- /*
Create chart name and version as used by the chart label.
*/}}
{{- define "ai-todo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- /*
Common labels
*/}}
{{- define "ai-todo.labels" -}}
helm.sh/chart: {{ include "ai-todo.chart" . }}
{{ include "ai-todo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- /*
Selector labels
*/}}
{{- define "ai-todo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-todo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- /*
Frontend labels
*/}}
{{- define "ai-todo.frontend.labels" -}}
{{ include "ai-todo.labels" . }}
app.kubernetes.io/component: frontend
app.kubernetes.io/part-of: ai-todo
{{- end }}

{{- /*
Frontend selector labels
*/}}
{{- define "ai-todo.frontend.selectorLabels" -}}
app.kubernetes.io/name: frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- /*
Backend labels
*/}}
{{- define "ai-todo.backend.labels" -}}
{{ include "ai-todo.labels" . }}
app.kubernetes.io/component: backend
app.kubernetes.io/part-of: ai-todo
{{- end }}

{{- /*
Backend selector labels
*/}}
{{- define "ai-todo.backend.selectorLabels" -}}
app.kubernetes.io/name: backend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
