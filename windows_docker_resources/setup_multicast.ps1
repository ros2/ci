# On Windows Server 2025, the HNS NAT endpoint (vEthernet (Ethernet)) does not support
# IP_ADD_MEMBERSHIP. The loopback does. Lower its 224.0.0.0/4 RouteMetric to 1 so it
# wins the route election over vEthernet (Ethernet)'s RouteMetric of 2.
$idx = (Get-NetIPInterface -InterfaceAlias 'Loopback Pseudo-Interface' `
    -AddressFamily IPv4 -ErrorAction SilentlyContinue).ifIndex
if ($idx) {
    Get-NetRoute -InterfaceIndex $idx -DestinationPrefix '224.0.0.0/4' `
        -ErrorAction SilentlyContinue | Remove-NetRoute -Confirm:$false -ErrorAction SilentlyContinue
    New-NetRoute -InterfaceIndex $idx -DestinationPrefix '224.0.0.0/4' `
        -NextHop '0.0.0.0' -RouteMetric 1 -AddressFamily IPv4 | Out-Null
}
