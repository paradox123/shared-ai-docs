#!/bin/bash

PILOT_CONFIGURATION_VARIABLES=(
    PILOT_EXECUTABLE CLOUDFLARED_EXECUTABLE CLOUDFLARED_CONFIG
    CLOUDFLARED_TUNNEL_NAME PILOT_GITHUB_WEBHOOK_URL PILOT_PUBLIC_RECEIVER_URL
    PILOT_HOST PILOT_PORT
    PILOT_ALLOWED_REPOSITORIES GITHUB_TOKEN DANIEL_GITHUB_LOGIN
    PILOT_REPOSITORY_ROOT PILOT_WORKTREE_ROOT PILOT_REPOSITORY_CONTEXT_PATH
    PILOT_PUBLIC_OBSERVATION_SURFACE PILOT_VERIFICATION_COMMAND PILOT_SKILL_ROOT
    PILOT_DATABASE_PATH PILOT_INTERNAL_WEBHOOK_SECRET GITHUB_WEBHOOK_SECRET
    PILOT_LAUNCH_AGENT_LABEL PILOT_BASE_REF PILOT_CODEX_EXECUTABLE
    PILOT_CODEX_INTERVENTION_SURFACE
    PILOT_CODEX_TIMEOUT_SECONDS PILOT_GIT_EXECUTABLE PILOT_MAX_REQUEST_BYTES
    PILOT_TEST_EFFECT_LOG
)

PILOT_REQUIRED_CONFIGURATION_VARIABLES=(
    PILOT_EXECUTABLE CLOUDFLARED_EXECUTABLE CLOUDFLARED_CONFIG
    CLOUDFLARED_TUNNEL_NAME PILOT_GITHUB_WEBHOOK_URL PILOT_PUBLIC_RECEIVER_URL PILOT_PORT
    PILOT_ALLOWED_REPOSITORIES GITHUB_TOKEN DANIEL_GITHUB_LOGIN
    PILOT_REPOSITORY_ROOT PILOT_WORKTREE_ROOT PILOT_REPOSITORY_CONTEXT_PATH
    PILOT_PUBLIC_OBSERVATION_SURFACE PILOT_VERIFICATION_COMMAND PILOT_SKILL_ROOT
    PILOT_DATABASE_PATH PILOT_INTERNAL_WEBHOOK_SECRET
    PILOT_CODEX_INTERVENTION_SURFACE
)

pilot_configuration_error() {
    printf 'configuration_status=invalid category=%s\n' "$1" >&2
    return 64
}

pilot_process_running() {
    local pid="$1"
    local process_state

    [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 1
    process_state="$(/bin/ps -p "$pid" -o state= 2>/dev/null)" || return 1
    [[ -n "$process_state" && "$process_state" != *Z* ]]
}

pilot_configuration_variable_allowed() {
    local requested="$1"
    local configured

    for configured in "${PILOT_CONFIGURATION_VARIABLES[@]}"; do
        [[ "$configured" == "$requested" ]] && return 0
    done
    return 1
}

pilot_require_private_environment() {
    local environment_file="$1"
    local owner mode mode_value

    if [[ ! -f "$environment_file" || -L "$environment_file" ]]; then
        pilot_configuration_error unsafe_environment_file
        return
    fi
    owner="$(/usr/bin/stat -f '%u' "$environment_file" 2>/dev/null)" || {
        pilot_configuration_error unsafe_environment_file
        return
    }
    if [[ "$owner" != "$(/usr/bin/id -u)" ]]; then
        pilot_configuration_error unsafe_environment_file
        return
    fi
    mode="$(/usr/bin/stat -f '%Lp' "$environment_file" 2>/dev/null)" || {
        pilot_configuration_error unsafe_permissions
        return
    }
    mode_value=$((8#$mode))
    if (( (mode_value & 077) != 0 )); then
        pilot_configuration_error unsafe_permissions
        return
    fi
}

pilot_load_environment() {
    local environment_file="$1"
    local line name value seen='|'

    pilot_require_private_environment "$environment_file" || return
    for name in "${PILOT_CONFIGURATION_VARIABLES[@]}"; do
        unset "$name"
    done
    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        [[ -z "$line" || "$line" == \#* ]] && continue
        if [[ ! "$line" =~ ^[A-Z][A-Z0-9_]*= ]]; then
            pilot_configuration_error invalid_syntax
            return
        fi
        name="${line%%=*}"
        value="${line#*=}"
        pilot_configuration_variable_allowed "$name" || {
            pilot_configuration_error invalid_syntax
            return
        }
        if [[ "$seen" == *"|$name|"* ]]; then
            pilot_configuration_error invalid_syntax
            return
        fi
        seen="$seen$name|"
        if [[ "$value" == \'* ]]; then
            if [[ ${#value} -lt 2 || "$value" != *\' ]]; then
                pilot_configuration_error invalid_syntax
                return
            fi
            value="${value:1:${#value}-2}"
            if [[ "$value" == *\'* ]]; then
                pilot_configuration_error invalid_syntax
                return
            fi
        elif [[ "$value" == \"* ]]; then
            if [[ ${#value} -lt 2 || "$value" != *\" ]]; then
                pilot_configuration_error invalid_syntax
                return
            fi
            value="${value:1:${#value}-2}"
            if [[ "$value" == *\"* ]]; then
                pilot_configuration_error invalid_syntax
                return
            fi
        fi
        export "$name=$value"
    done < "$environment_file"
}

pilot_require_variables() {
    local name
    for name in "${PILOT_REQUIRED_CONFIGURATION_VARIABLES[@]}"; do
        if [[ -z "${!name:-}" ]]; then
            pilot_configuration_error missing_variable
            return
        fi
    done
}

pilot_validate_absolute_paths() {
    local path
    for path in \
        "$PILOT_EXECUTABLE" \
        "$CLOUDFLARED_EXECUTABLE" \
        "$CLOUDFLARED_CONFIG" \
        "$PILOT_REPOSITORY_ROOT" \
        "$PILOT_WORKTREE_ROOT" \
        "$PILOT_REPOSITORY_CONTEXT_PATH" \
        "$PILOT_SKILL_ROOT" \
        "$PILOT_DATABASE_PATH"
    do
        if [[ "$path" != /* ]]; then
            pilot_configuration_error invalid_absolute_path
            return
        fi
    done
    if [[ ! -x "$PILOT_EXECUTABLE" || ! -x "$CLOUDFLARED_EXECUTABLE" ]]; then
        pilot_configuration_error invalid_executable
        return
    fi
    if [[ ! -f "$CLOUDFLARED_CONFIG" ]]; then
        pilot_configuration_error invalid_tunnel_config
        return
    fi
}

pilot_validate_receiver() {
    if [[ "${PILOT_HOST:-127.0.0.1}" != "127.0.0.1" ]]; then
        pilot_configuration_error unsafe_receiver_host
        return
    fi
    if [[ ! "$PILOT_PUBLIC_RECEIVER_URL" =~ ^https://[^/?#]+/webhooks/github$ ]]; then
        pilot_configuration_error unsafe_receiver_url
        return
    fi
    if [[ ! "$PILOT_GITHUB_WEBHOOK_URL" =~ ^https://[^/?#]+/webhooks/github$ ||
        "$PILOT_GITHUB_WEBHOOK_URL" == "$PILOT_PUBLIC_RECEIVER_URL" ]]; then
        pilot_configuration_error unsafe_webhook_url
        return
    fi
    if [[ ! "$PILOT_PORT" =~ ^[0-9]+$ ]] || (( PILOT_PORT < 1 || PILOT_PORT > 65535 )); then
        pilot_configuration_error invalid_receiver_port
        return
    fi
    if [[ -n "${GITHUB_WEBHOOK_SECRET:-}" ]]; then
        pilot_configuration_error conflicting_authentication
        return
    fi
    export PILOT_HOST=127.0.0.1
}

pilot_validate_tunnel() {
    "$CLOUDFLARED_EXECUTABLE" tunnel --config "$CLOUDFLARED_CONFIG" \
        ingress validate >/dev/null 2>&1 || {
        pilot_configuration_error tunnel_validation_failed
        return
    }
    "$CLOUDFLARED_EXECUTABLE" tunnel --config "$CLOUDFLARED_CONFIG" \
        ingress rule "$PILOT_PUBLIC_RECEIVER_URL" >/dev/null 2>&1 || {
        pilot_configuration_error tunnel_validation_failed
        return
    }
}

pilot_validate_configuration() {
    local environment_file="$1"

    pilot_load_environment "$environment_file" || return
    pilot_require_variables || return
    pilot_validate_absolute_paths || return
    pilot_validate_receiver || return
    if [[ "$PILOT_CODEX_INTERVENTION_SURFACE" != "stable-app-server" ]]; then
        pilot_configuration_error unsupported_intervention_surface
        return
    fi
    pilot_validate_tunnel || return
}
