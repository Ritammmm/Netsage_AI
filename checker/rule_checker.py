def check_duplicate_ip(ip_list):

    if len(ip_list) != len(set(ip_list)):
        return "Duplicate IP detected"

    return "No duplicate IP"


def check_gateway(ip, gateway):

    network = ip.split(".")[0:3]
    gateway_network = gateway.split(".")[0:3]

    if network != gateway_network:
        return "Gateway mismatch"

    return "Gateway is correct"


def check_interface(status):

    status = status.lower()

    if status in ["down", "notconnect"]:
        return "Interface is down"

    return "Interface is active"


def check_subnet_mask(mask):

    correct_mask = "255.255.255.0"

    if mask != correct_mask:
        return "Wrong subnet mask detected"

    return "Subnet mask is correct"


def check_vlan(device_vlan, expected_vlan):

    if device_vlan != expected_vlan:
        return "Missing or incorrect VLAN"

    return "VLAN configuration correct"


def check_route(required_network, routing_table):

    if required_network not in routing_table:
        return "Missing route detected"

    return "Route exists"


def run_rule_checks(symptom, topology, evidence):

    findings = []

    evidence_lower = evidence.lower()
    symptom_lower = symptom.lower()

    # Interface check
    if "notconnect" in evidence_lower:
        findings.append(
            "Rule Checker: Interface shows notconnect - physical link issue suspected"
        )

    elif "interface" in symptom_lower and "down" in evidence_lower:
        findings.append(
            "Rule Checker: Interface is down"
        )

    # Duplicate IP check
    if "duplicate ip" in symptom_lower:
        findings.append(
            "Rule Checker: Duplicate IP should be investigated"
        )

    # Gateway check
    if "gateway" in symptom_lower:
        findings.append(
            "Rule Checker: Gateway configuration should be verified"
        )

    # VLAN check
    if "vlan" in symptom_lower or "vlan" in evidence_lower:
        findings.append(
            "Rule Checker: VLAN configuration should be verified"
        )

    # Routing check
    if "route" in symptom_lower or "routing" in symptom_lower:
        findings.append(
            "Rule Checker: Routing table should be verified"
        )

    # Subnet mask check
    if "subnet" in symptom_lower or "subnet mask" in evidence_lower:
        findings.append(
            "Rule Checker: Subnet mask should be verified"
        )

    if not findings:
        findings.append(
            "Rule Checker: No deterministic rule matched the available evidence"
        )

    return findings