//////////////////////////////////////////////////////////////////////////////
// GF Agent-Safety YARA rules
//
// Foundation-specific detections layered on top of cisco-ai-skill-scanner's
// built-in rules. Derived from the skill-vetter RED FLAGS
// (clawhub.ai/spclaudehome/skill-vetter).
//
// Loaded in CI via:  skill-scanner scan-all . --custom-rules scanner/custom-yara
//
// These cover the three checks not already handled by the scanner's built-in
// rules: agent-memory/identity theft, raw-IP exfiltration, and browser-data
// theft. The other skill-vetter red flags (curl/wget, credential prompts,
// system-file writes, silent installs, base64, eval/exec, sudo, obfuscation)
// are covered by the scanner's built-in signature + behavioral engines.
//////////////////////////////////////////////////////////////////////////////

rule vetter_agent_memory_theft {

    meta:
        author = "GF AI Skills (derived from skill-vetter)"
        description = "Detects skills that read agent memory, identity, or personality files to steal context or impersonate the agent"
        classification = "harmful"
        threat_type = "AGENT MEMORY THEFT"

    strings:
        // Agent memory / identity files
        $memory_md    = "MEMORY.md" nocase
        $user_md      = "USER.md" nocase
        $soul_md      = "SOUL.md" nocase
        $identity_md  = "IDENTITY.md" nocase

        // Claude Code-specific config / memory paths
        $claude_memory   = ".claude/memory" nocase
        $claude_settings = ".claude/settings" nocase
        $claude_config   = "claude_desktop_config.json" nocase

        // File-access actions
        $open_call  = /\b(open|read|cat|head|tail)\s*\(/
        $path_read  = /Path\s*\([^)]+\)\.(read_text|read_bytes)/

        // Exclude: documentation references
        $doc_ref = /(README|CHANGELOG|CONTRIBUTING|LICENSE)/i

    condition:
        not $doc_ref and
        (
            // any agent file name + a file-read action
            (
                ($memory_md or $user_md or $soul_md or $identity_md) and
                ($open_call or $path_read)
            )
            or
            // Claude config/memory paths (dangerous with or without an open call)
            $claude_memory or
            $claude_settings or
            $claude_config
        )
}

rule vetter_ip_exfiltration {

    meta:
        author = "GF AI Skills (derived from skill-vetter)"
        description = "Detects network calls to raw IP addresses instead of domain names, which may bypass DNS logging and content filtering"
        classification = "harmful"
        threat_type = "IP-BASED EXFILTRATION"

    strings:
        // HTTP request to an IP address
        $http_ip = /https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/

        // Socket connection to an IP
        $socket_ip = /connect\s*\(\s*\(?\s*['\"]\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/

        // curl/wget to an IP
        $curl_ip = /\b(curl|wget)\s+[^\n]*https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/

        // Exclude: private ranges and local addresses
        $private_10     = /https?:\/\/10\.\d{1,3}\.\d{1,3}\.\d{1,3}/
        $private_172    = /https?:\/\/172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}/
        $private_192    = /https?:\/\/192\.168\.\d{1,3}\.\d{1,3}/
        $loopback       = /https?:\/\/127\.0\.0\.1/
        $any_addr       = /https?:\/\/0\.0\.0\.0/
        $doc_comment    = /^(\s*#|\s*\/\/|\s*\*)/

    condition:
        not $private_10 and
        not $private_172 and
        not $private_192 and
        not $loopback and
        not $any_addr and
        not $doc_comment and
        (
            $http_ip or
            $socket_ip or
            $curl_ip
        )
}

rule vetter_browser_data_theft {

    meta:
        author = "GF AI Skills (derived from skill-vetter)"
        description = "Detects skills that access browser cookies, sessions, saved passwords, or profile data"
        classification = "harmful"
        threat_type = "BROWSER DATA THEFT"

    strings:
        // Browser data paths
        $chrome_path   = /Google\/Chrome\/(Default|Profile)/ nocase
        $firefox_path  = /\.mozilla\/firefox\/[^\s]*profiles/ nocase
        $brave_path    = "BraveSoftware" nocase
        $chromium_path = /Chromium\/(Default|Profile)/ nocase
        $edge_path     = "Microsoft/Edge" nocase

        // macOS path
        $mac_chrome = "Library/Application Support/Google/Chrome" nocase

        // Cookie / session database files
        $cookies_db      = "Cookies" nocase
        $login_data      = "Login Data" nocase
        $web_data        = "Web Data" nocase
        $local_storage   = "Local Storage" nocase
        $session_storage = "Session Storage" nocase

        // sqlite3 opening a browser DB
        $sqlite_cookies = /sqlite3[^\n]*(Cookies|Login Data|Web Data)/i

        // Exclude
        $set_cookie = /Set-Cookie/i
        $cookie_policy = /cookie[_\s]?policy/i
        $documentation = /(```|README|CHANGELOG)/i

    condition:
        not $set_cookie and
        not $cookie_policy and
        not $documentation and
        (
            // browser path access
            $chrome_path or
            $firefox_path or
            $brave_path or
            $chromium_path or
            $edge_path or
            $mac_chrome or

            // browser DB file + sqlite
            $sqlite_cookies or

            // browser DB file name + browser path (must co-occur)
            (
                ($cookies_db or $login_data or $web_data) and
                ($chrome_path or $firefox_path or $mac_chrome or $chromium_path)
            )
        )
}
