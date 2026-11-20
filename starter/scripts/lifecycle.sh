#!/usr/bin/env bash
set -euo pipefail
url="http://127.0.0.1:${PORT:-8000}/mcp"
version=2025-11-25
headers=(-H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream')
post() {
  curl -q --noproxy '*' -fsS --max-time 10 "${headers[@]}" --data "$1" "$url"
}

# 1. Согласуем версию протокола
init=$(post "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"$version\",\"capabilities\":{},\"clientInfo\":{\"name\":\"club-curl\",\"version\":\"1\"}}}")
printf '%s\n' "$init" | jq -e --arg v "$version" '.result.protocolVersion | select(. == $v)'
headers+=(-H "MCP-Protocol-Version: $version")
# 2. Уведомление без id, в ответ только HTTP 202
status=$(curl -q --noproxy '*' -fsS --max-time 10 "${headers[@]}" -o /dev/null -w '%{http_code}' \
  --data '{"jsonrpc":"2.0","method":"notifications/initialized"}' "$url")
printf 'notifications/initialized: %s\n' "$status"
[[ $status == 202 ]]
# 3. Находим оба инструмента
post '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | jq -e '[.result.tools[].name] | sort | select(index("lookup_club_room") != null and index("ping") != null)'
# 4. Вызываем ping, затем поиск аудитории
post '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"ping","arguments":{}}}' | jq -e '.result | select(.isError != true) | .content[0].text | select(. == "pong")'
post '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"lookup_club_room","arguments":{"club_id":"orbit"}}}' | jq -e '.result | {isError, content}'
post '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"lookup_club_room","arguments":{"club_id":"missing"}}}' | jq -e '.result | {isError, content}'
