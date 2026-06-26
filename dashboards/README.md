# Dashboard: Rede - Monitoramento de Equipamentos (Zabbix)

Dashboard Grafana para monitorar Mikrotik, switches, roteadores e APs Unifi cujos dados chegam via plugin **Zabbix** (Alexander Zobnin, `alexanderzobnin-zabbix-datasource`).

## Pré-requisitos

- Datasource Zabbix configurado no Grafana com o nome **`Zabbix`** (se o seu tiver outro nome, ajuste após importar — ver "Ajustes pós-import").
- Todos os equipamentos cadastrados no Zabbix dentro do grupo de host **`Rede`**.
- Itens padrão do template Zabbix (ICMP ping, CPU utilization, Memory utilization, Interface ... Bits received/sent, Uptime). Os nomes exatos dos itens variam por template/versão — se os painéis vierem vazios, confira o nome real do item no Zabbix e ajuste o filtro regex do painel (campo `item.filter`).
- Para a row "Mikrotik": os itens de sessão BGP vêm da discovery feita pelo script [`network-and-routing/mikrotik_bgp_peer_lld.sh`](../../network-and-routing/mikrotik_bgp_peer_lld.sh). Os painéis de **VPN ativa**, **conexões de firewall** e **status de redundância de uplink** são *placeholders* — não existem itens Zabbix nativos para isso; é necessário criar scripts de coleta customizados (semelhantes aos demais scripts deste repositório) antes desses painéis mostrarem dados reais.

## Como importar

1. No Grafana: **Dashboards → New → Import**.
2. Faça upload do arquivo `network-equipment-overview.json` ou cole o conteúdo.
3. Selecione o datasource Zabbix quando solicitado.
4. Importar.

## Ajustes pós-import (obrigatório na primeira vez)

O grupo de host está fixo como `Rede` (variável `group`). Caso seu grupo tenha outro nome, edite a variável `group` nas configurações do dashboard (Dashboard settings → Variables).

Como o Zabbix está com todos os equipamentos em um único grupo, o dashboard usa variáveis seletoras de host (tipo `custom`, já pré-preenchidas com os nomes reais informados):

- `mikrotik_hosts` — `Mk Galpao`, `Mk-Firewall`
- `switch_router_hosts` — `Switch Rack 803`, `Switch Rack 902`, `Switch Rack 906`, `TESTI-BR-902`
- `ap_hosts` — os 6 APs `U7 Pro - ...`
- `vpn_mikrotik_host` — fixo em `Mk-Firewall` (o Mikrotik que concentra firewall/VPN)

Se algum host for renomeado ou um novo equipamento for adicionado, edite a lista de opções da variável correspondente em Dashboard settings → Variables.

> Dica: tags no Zabbix (ex. `device_type: mikrotik`) continuam úteis para sua organização interna, só não são o mecanismo técnico de filtro deste dashboard (suporte a filtro de host por tag é instável entre versões do plugin Zabbix-Grafana).

## Itens Zabbix usados — confira os nomes reais

Os filtros de item abaixo assumem nomes de templates oficiais/comuns do Zabbix. Se um painel não mostrar dados, confira o nome exato em **Data collection → Hosts → Items** no host correspondente e ajuste o campo `item.filter` do painel (regex):

| Painel | Filtro assumido | Observação |
|---|---|---|
| Status (ICMP) | `ICMP ping` | Template oficial "ICMP Ping" — **confira se esse template está de fato vinculado aos hosts de switch/AP**, além do template SNMP do fabricante; senão o item não existe e o painel fica vazio |
| Latência ICMP | `ICMP response time` | Corrigido — não é "ICMP ping response time" |
| CPU/Memória (switches/roteadores) | `CPU utilization` / `.*Memory utilization` | Confirmado no template oficial **HP Enterprise Switch by SNMP**: CPU é item único "CPU utilization"; Memória é descoberta por módulo, nome "`<módulo>: Memory utilization`" |
| CPU do AP | `CPU Usage` / `CPU AVG Load` | Confirmado no template **Ubiquiti UniFi SNMPv3**. Esse template **não tem item de memória nem temperatura** — painel removido/sem dado nesses dois |
| Clientes conectados (AP) | `Users {SSID} on {Radio}` | Confirmado no template Ubiquiti UniFi SNMPv3 — item é por SSID/rádio (descoberto via LLD "Wifi Virtual Interfaces"), não existe um total único |
| Tráfego do AP | `LAN Traffic Incoming/Outgoing (bits)` | Confirmado no template Ubiquiti UniFi SNMPv3 — nome próprio, não segue o padrão genérico "Interface ...: Bits sent/received" |
| Tráfego WAN (Mikrotik) | `Interface (ether1\|ether2)...: Bits received/sent` | Ajustado para nomenclatura padrão RouterOS (sem "WAN" no nome da interface) |
| Peers WireGuard (status/tráfego) | `Interface wg-<nome>(): Operational status` / `Bits received\|sent` | Descoberto pelo discovery genérico de interface do Zabbix (mesmo mecanismo do ether1/ether2), não precisa de script customizado |
| Sessões OpenVPN (status/tráfego) | `Interface <ovpn-usuario>(): Operational status` / `Bits received\|sent` | Idem — discovery genérico de interface |
| Erros/drops VPN | `Interface (wg-...\|<ovpn-...>)(): Inbound/Outbound packets discarded\|errors` | Mesmos contadores de erro de interface usados na row de switches |

## Mikrotik - Redundância, Firewall, BGP e VPN

- **WireGuard e OpenVPN (Mk-Firewall)**: o Zabbix já descobre essas VPNs automaticamente como interfaces de rede comuns (discovery genérico de interface, o mesmo que descobre `ether1`/`ether2`). Não é necessário nenhum script ou discovery rule adicional — os painéis 50–54 já usam esse padrão de nome. Confirmado: WireGuard aparece como `Interface wg-<nome>()`, OpenVPN como `Interface <ovpn-usuario>()`.
  - Os scripts [`mikrotik_wireguard_peer_lld.sh`](../../network-and-routing/mikrotik_wireguard_peer_lld.sh), [`mikrotik_ovpn_session_lld.sh`](../../network-and-routing/mikrotik_ovpn_session_lld.sh) e [`mikrotik_ovpn_session_traffic.sh`](../../network-and-routing/mikrotik_ovpn_session_traffic.sh) ficam no repositório como **opcionais**, só fazem sentido se você quiser metadados que o discovery genérico de interface não traz (ex.: `last-handshake` do WireGuard, ou identificar a sessão OpenVPN pelo `caller-id`/IP real do cliente).
- **Redundância de uplink (placeholder)**: não existe item nativo. Requer item de "Operational status" de cada interface WAN (já cobertos pelo discovery genérico de interface, ver painel 33) **ou** um item de Netwatch/Check Gateway customizado — não criado ainda, fora do escopo desta rodada.

### Setup pendente no Zabbix (3 itens — passo a passo)

> ⚠️ **Atenção**: "Regras de descoberta" (LLD) aqui **não é** o menu "Dados coletados → Descoberta" (esse é Network Discovery, escaneamento de faixa de IP para achar hosts novos — feature diferente). As LLD rules usadas abaixo ficam **dentro do host**, na lista de Hosts.

Estes 3 painéis seguem vazios porque os itens correspondentes **ainda não existem no Zabbix**. Use o padrão "External check" descrito no [`README.md`](../../README.md) principal do repositório (seção "API Polling & Integrations: External Checks").

**1) Status (ICMP) vazio em switches e APs, e "Status do AP"**
Causa provável: o template **ICMP Ping** não está vinculado a esses hosts (só o template SNMP do fabricante está). Para cada host de switch e AP:
1. **Dados coletados → Hosts** → clique no nome do host (ex. `Switch Rack 803`) para abrir a configuração.
2. Na aba **Templates**, em "Link new templates" / "Vincular novos templates", busque **ICMP Ping** e adicione.
3. Clique em **Update / Atualizar**.
4. Repita para os demais switches e os 6 APs. Aguarde 1 intervalo de coleta (padrão 1m) e confira em **Monitoramento → Últimos dados**.

**2) Sessões BGP (painel 34) — regra de descoberta (LLD) por host, ainda não criada**
1. Copie `network-and-routing/mikrotik_bgp_peer_lld.sh` para `/usr/lib/zabbix/externalscripts/` no Zabbix Server/Proxy, dê permissão de execução (`chmod +x`, owner `zabbix`).
2. **Dados coletados → Hosts** → na linha do host Mikrotik (ex. `Mk-Firewall`), clique no link **"Regras de descoberta"** (coluna de contadores, ao lado de "Itens"/"Disparadores") → **Criar regra de descoberta** (botão no canto superior direito dessa tela, não no menu lateral "Descoberta").
   - Nome: `Descoberta de peers BGP`
   - Tipo: **Verificação externa (External check)**
   - Chave: `mikrotik_bgp_peer_lld.sh["{$MIKROTIK_IP}","{$MIKROTIK_USER}","{$MIKROTIK_PASS}"]` (crie essas macros na aba **Macros** do host; `{$MIKROTIK_PASS}` como tipo **Texto secreto**)
   - Tipo de informação: **Texto**
   - Intervalo de atualização: `1m` (ou maior)
3. Dentro dessa regra de descoberta, aba **Protótipos de item**, crie:
   - Nome: `BGP peer {#PEER_NAME}: state` | Tipo: **Item dependente** | Item mestre: a própria regra de descoberta | Pré-processamento: **JSONPath** — teste com um payload de exemplo do script para o Zabbix sugerir o caminho correto (geralmente `$.state` aplicado ao elemento do array já filtrado pelo macro `{#PEER_NAME}`).
4. Salve e aguarde a próxima execução.

**3) Túneis VPN ativos (painel 35) e Conexões de firewall ativas (painel 36) — itens novos**
1. Copie `network-and-routing/mikrotik_vpn_tunnels_count.sh` e `network-and-routing/mikrotik_firewall_active_connections.sh` para `/usr/lib/zabbix/externalscripts/` (mesma permissão do passo anterior).
2. **Dados coletados → Hosts** → na linha do host `Mk-Firewall`, clique no link **"Itens"** → **Criar item** (canto superior direito).
   - Item 1 — Nome: **`VPN tunnels active count`** | Tipo: **Verificação externa** | Chave: `mikrotik_vpn_tunnels_count.sh["{$MIKROTIK_IP}","{$MIKROTIK_USER}","{$MIKROTIK_PASS}"]` | Tipo de informação: **Numérico (não-assinado)**
   - Item 2 — Nome: **`Firewall active connections`** | Tipo: **Verificação externa** | Chave: `mikrotik_firewall_active_connections.sh["{$MIKROTIK_IP}","{$MIKROTIK_USER}","{$MIKROTIK_PASS}"]` | Tipo de informação: **Numérico (não-assinado)**
3. Os nomes dos itens precisam ser exatamente esses (`VPN tunnels active count` / `Firewall active connections`) porque os painéis 35/36 do dashboard já filtram por esse texto. Se preferir outro nome, ajuste o campo `item.filter` desses painéis no JSON.

## Estrutura

| Row | Conteúdo |
|---|---|
| Visão Geral / Disponibilidade | Status ICMP, latência, uptime — todos os hosts do grupo `Rede` |
| Switches & Roteadores | Tráfego de interface, erros/drops, CPU, memória |
| AP Unifi | Status, clientes conectados, tráfego, CPU/memória/temperatura |
| Mikrotik | Status, CPU/memória/temperatura, tráfego por link WAN (ether1/ether2), redundância de uplink (placeholder), sessões BGP, VPN ativa (placeholder), conexões de firewall (placeholder) |
| VPN (WireGuard / OpenVPN) - Mk-Firewall | Peers WireGuard conectados, velocidade RX/TX por peer, sessões OpenVPN conectadas, velocidade RX/TX por sessão, erros/drops por sessão OpenVPN |
