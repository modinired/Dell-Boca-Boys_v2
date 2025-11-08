#!/usr/bin/env bash
# Interactive CLI wrapper for the Chiccki face agent.
# Provides a quick prompt loop that sends workflow requests to the API
# and echoes back persona-influenced summaries.

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "Chiccki> Missing dependency: install jq (brew install jq)." >&2
  exit 1
fi

API_BASE=${CHICCKI_API_BASE:-http://localhost:8080}
PERSONA=${CHICCKI_PERSONA:-terry}
AUTO_STAGE=${CHICCKI_AUTO_STAGE:-false}
AUTO_ACTIVATE=${CHICCKI_AUTO_ACTIVATE:-false}
OUTPUT_MODE=${CHICCKI_OUTPUT_MODE:-summary}

show_help() {
  cat <<'CHICCKI_HELP'
Commands:
  /persona <key>     switch persona (e.g. terry, formal)
  /stage on|off      toggle auto staging in n8n
  /activate on|off   toggle auto activation (implies staging)
  /output summary    show persona message (default)
  /output qa         show QA summary and score
  /output raw        print full JSON response
  /knowledge <q>     semantic search of knowledge base
  /rebuild <id>      restage a workflow ID in n8n
  /summary [period]  display recap (daily/weekly/monthly)
  /help              show this help
  /exit              quit the session
CHICCKI_HELP
}

format_bool() {
  [[ $1 == true ]] && echo on || echo off
}

printf "Ey, yo! Chiccki here. Hit enter on an empty prompt to bounce.\n"
printf "Type /help for commands. Persona: %s | staging: %s | activation: %s | output: %s\n" \
  "$PERSONA" "$(format_bool "$AUTO_STAGE")" "$(format_bool "$AUTO_ACTIVATE")" "$OUTPUT_MODE"

while true; do
  read -rp "You> " USER_INPUT || break

  if [[ -z "${USER_INPUT// }" ]]; then
    echo "Chiccki> Alright, Bobby-boy, catch you later."
    break
  fi

  if [[ $USER_INPUT == /* ]]; then
    cmd=${USER_INPUT%% *}
    args=${USER_INPUT#${cmd}}
    args=${args## }
    case "$cmd" in
      /persona)
        if [[ -z "$args" ]]; then
          echo "Chiccki> Need a persona key, capisce?"
        else
          PERSONA=$args
          echo "Chiccki> Persona locked to '$PERSONA'."
        fi
        ;;
      /stage)
        if [[ $args == on ]]; then
          AUTO_STAGE=true
          echo "Chiccki> We'll auto-stage in n8n."
        elif [[ $args == off ]]; then
          AUTO_STAGE=false
          AUTO_ACTIVATE=false
          echo "Chiccki> No more auto-staging."
        else
          echo "Chiccki> Say 'on' or 'off' for staging."
        fi
        ;;
      /activate)
        if [[ $args == on ]]; then
          AUTO_STAGE=true
          AUTO_ACTIVATE=true
          echo "Chiccki> We'll stage and flip it live."
        elif [[ $args == off ]]; then
          AUTO_ACTIVATE=false
          echo "Chiccki> Activation stays manual."
        else
          echo "Chiccki> Use 'on' or 'off' for activation."
        fi
        ;;
      /output)
        case "$args" in
          summary|qa|raw)
            OUTPUT_MODE=$args
            echo "Chiccki> Output mode switched to $OUTPUT_MODE."
            ;;
          "")
            echo "Chiccki> Current mode: $OUTPUT_MODE."
            ;;
          *)
            echo "Chiccki> Options are summary, qa, or raw."
            ;;
        esac
        ;;
      /help)
        show_help
        ;;
      /knowledge)
        if [[ -z "$args" ]]; then
          echo "Chiccki> Toss me a query, Bobby-boy."
          continue
        fi
        response=$(curl -sS -X POST "$API_BASE/api/v1/knowledge/search" \
          -H 'Content-Type: application/json' \
          -d "{\"query\": \"$args\", \"top_k\": 5}") || {
            echo "Chiccki> Can't reach the KB."
            continue
        }
        if [[ $(jq -r '.success // false' <<<"$response") != true ]]; then
          msg=$(jq -r '.detail // .error // "Search failed"' <<<"$response")
          echo "Chiccki> $msg"
        else
          jq -r '.results[] | "- [\(.source)] \(.title // "untitled"): \(.chunk_text[:160])..."' <<<"$response"
        fi
        ;;
      /rebuild)
        if [[ -z "$args" ]]; then
          echo "Chiccki> Need a workflow ID to restage."
          continue
        fi
        response=$(curl -sS -X POST "$API_BASE/api/v1/deployment/stage?workflow_id=$args" ) || {
            echo "Chiccki> Couldn't hit deployment endpoint."
            continue
        }
        if [[ $(jq -r '.success // false' <<<"$response") != true ]]; then
          msg=$(jq -r '.detail // .error // "Stage failed"' <<<"$response")
          echo "Chiccki> $msg"
        else
          echo "Chiccki> Restaged workflow $args."
        fi
        ;;
      /summary)
        period=${args:-daily}
        response=$(curl -sS -X POST "$API_BASE/api/v1/journal/generate" \
          -H 'Content-Type: application/json' \
          -d "{\"period\": \"$period\"}") || {
            echo "Chiccki> Couldn't hit the journal endpoint."
            continue
        }
        ok=$(jq -r '.success // false' <<<"$response")
        if [[ $ok != true ]]; then
          msg=$(jq -r '.detail // .error // "No summary available"' <<<"$response")
          echo "Chiccki> $msg"
        else
          summary=$(jq -r '.summary.summary' <<<"$response")
          thought=$(jq -r '.summary.daily_thought // empty' <<<"$response")
          echo "Chiccki> Recap ($period): $summary"
          [[ -n "$thought" ]] && echo "Chiccki> Thought: $thought"
        fi
        ;;
      /exit)
        echo "Chiccki> We're done here."
        break 2
        ;;
      *)
        echo "Chiccki> Unknown command. Try /help."
        ;;
    esac
    continue
  fi

  payload=$(jq -n \
    --arg goal "$USER_INPUT" \
    --arg persona "$PERSONA" \
    --argjson stage "$AUTO_STAGE" \
    --argjson activate "$AUTO_ACTIVATE" \
    '(
      {
        user_goal: $goal,
        auto_stage: $stage,
        auto_activate: $activate
      }
      + (if ($persona | length) > 0 then {persona: $persona} else {} end)
    )')

  if ! response=$(curl -sS -X POST "$API_BASE/api/v1/workflow/design" \
      -H 'Content-Type: application/json' \
      -d "$payload"); then
    echo "Chiccki> Couldn't reach the API, check if it's running."
    continue
  fi

  success=$(jq -r '.success // false' <<<"$response") || success=false

  if [[ $success != true ]]; then
    error_msg=$(jq -r '.error // .message // "Request failed"' <<<"$response")
    echo "Chiccki> Fuggedaboutit—$error_msg"
    continue
  fi

  case "$OUTPUT_MODE" in
    summary)
      message=$(jq -r '.face_agent_message // "Workflow draft ready."' <<<"$response")
      echo "Chiccki> $message"
      ;;
    qa)
      qa_score=$(jq -r '.qa_results.quality_score // "N/A"' <<<"$response")
      node_count=$(jq -r '.provenance.node_count // "?"' <<<"$response")
      wf_id=$(jq -r '.workflow_id' <<<"$response")
      echo "Chiccki> QA score: $qa_score | Nodes: $node_count | Workflow ID: $wf_id"
      ;;
    raw)
      echo "$response" | jq
      ;;
  esac

  if [[ $OUTPUT_MODE != raw ]]; then
    n8n_link=$(jq -r '.deployment.n8n_workflow_id // empty' <<<"$response")
    if [[ -n "$n8n_link" ]]; then
      echo "Chiccki> Staged in n8n with ID $n8n_link."
    fi
  fi

done
