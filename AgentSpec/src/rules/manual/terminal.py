'''
Goal: Demonstrate different tools agents use in active-state to determine if tool
is destructive or not.
Ex: is_destructive -> ls (false) vs. rm -rf (true).

Pattern design rules:
  - All entries are raw regex strings passed to re.search().
  - Use \b word boundaries to avoid substring collisions:
      "cp" matches "script", "scp"; r"\bcp\b" does not.
  - Always-destructive commands: r"\b<cmd>\b" is enough.
  - Conditionally-destructive commands need compound patterns that include
    the dangerous flag or argument so safe invocations aren't flagged:
      find (safe) vs. find . -delete (destructive) -> r"\bfind\b.*-delete\b"
      tee -a (safe append) vs. tee (overwrites)    -> r"\btee\b(?!.*\s+-a\b)"
      sed (safe read) vs. sed -i (in-place edit)   -> r"\bsed\b.*-i\b"
  - Pipe-to-shell sequences are their own compound pattern:
      r"\b(curl|wget)\b[^|#\n]*\|\s*(ba|da|z)?sh\b"
'''
import re

# Each set is a collection of regex patterns for one category of destructiveness.
# re.search() is used, so patterns match anywhere in the command string.
# \b = word boundary — prevents partial matches (e.g. "rm" won't match "remove").

_DELETION_PATTERNS = {
    # Always-destructive removers
    r"\brm\b",
    r"\brmdir\b",
    r"\bunlink\b",
    r"\bshred\b",
    r"\bwipe\b",
    r"\bsrm\b",
    r"\bsfill\b",
    r"\bsswap\b",
    r"\bsdmem\b",
    r"\bsecure-delete\b",
    r"\bbleachbit\b",
    r"\bfstrim\b",
    r"\btruncate\b",

    # dd is only destructive when writing to an output target (of=)
    r"\bdd\b.*\bof=",

    # badblocks is only destructive in write-test mode (-w)
    r"\bbadblocks\b.*-w\b",

    # hdparm secure-erase wipes the drive
    r"\bhdparm\b.*--security-erase",

    # find is safe by default; only destructive with -delete or -exec rm
    r"\bfind\b.*-delete\b",
    r"\bfind\b.*-exec\s+rm\b",
}

_OVERWRITE_PATTERNS = {
    # Single > redirect overwrites the destination file.
    # Negative lookbehind/ahead excludes >> (append) and >= (comparison).
    r"(?<![>])>(?![>=])",

    # tee overwrites unless -a (append) is present
    r"\btee\b(?!.*\s+-a\b)",

    # dd is also an overwriter when of= is given (shared with _DELETION_PATTERNS)
    r"\bdd\b.*\bof=",

    # cp and mv silently overwrite the destination
    r"\bcp\b",
    r"\bmv\b",

    # install clobbers target files by design
    r"\binstall\b",

    # sponge buffers all stdin then atomically writes — overwrites target
    r"\bsponge\b",

    # sed/perl in-place flags rewrite the file on disk
    r"\bsed\b.*-i\b",
    r"\bperl\b.*-i\b",

    # fallocate can punch holes (FALLOC_FL_PUNCH_HOLE) over existing data
    r"\bfallocate\b",

    # hdparm --write-sector writes raw sectors
    r"\bhdparm\b.*--write-sector",

    # Non-interactive line editors — overwrite when used in scripts
    r"\bex\b",
    r"\bed\b",
}

_PERMISSION_PATTERNS = {
    # File permission & ownership
    r"\bchmod\b",
    r"\bchown\b",
    r"\bchgrp\b",
    r"\bumask\b",

    # Extended attributes & ACLs
    r"\bsetfacl\b",
    r"\bchacl\b",
    r"\bchattr\b",          # e.g. chattr +i (immutable), +a (append-only)

    # Capabilities
    r"\bsetcap\b",

    # User & group management
    r"\buseradd\b",
    r"\buserdel\b",
    r"\busermod\b",
    r"\badduser\b",
    r"\bdeluser\b",
    r"\bgroupadd\b",
    r"\bgroupdel\b",
    r"\bgroupmod\b",
    r"\baddgroup\b",
    r"\bdelgroup\b",
    r"\bnewgrp\b",
    r"\bgpasswd\b",

    # Password & authentication
    r"\bpasswd\b",
    r"\bchpasswd\b",
    r"\bchage\b",
    r"\bpam-auth-update\b",

    # Privilege escalation / identity switching
    r"\bsudo\b",
    r"\bsu\b",
    r"\brunuser\b",
    r"\bpkexec\b",
    r"\bvisudo\b",

    # SSH & key-based access
    r"\bssh-keygen\b",
    r"\bssh-copy-id\b",
    r"\bauthorized_keys\b",

    # SELinux / AppArmor
    r"\bchcon\b",
    r"\bsemanage\b",
    r"\brestorecon\b",
    r"\baa-enforce\b",
    r"\baa-complain\b",
    r"\baa-disable\b",
}

_SYSTEM_MUTATION_PATTERNS = {
    # Service & init management
    r"\bsystemctl\b",
    r"\bservice\b",
    r"\binit\b",
    r"\btelinit\b",
    r"\brc-service\b",
    r"\brc-update\b",

    # Package managers
    r"\bapt\b",
    r"\bapt-get\b",
    r"\bapt-cache\b",
    r"\bdpkg\b",
    r"\baptitude\b",
    r"\byum\b",
    r"\bdnf\b",
    r"\brpm\b",
    r"\bpacman\b",
    r"\bmakepkg\b",
    r"\byay\b",
    r"\bparu\b",
    r"\bzypper\b",
    r"\bsnap\b",
    r"\bflatpak\b",
    r"\bbrew\b",
    r"\bnix\b",
    r"\bnix-env\b",
    r"\bguix\b",

    # Language-level package managers (can run arbitrary install scripts)
    r"\bpip\b",
    r"\bpip3\b",
    r"\bpipx\b",
    r"\bnpm\b",
    r"\byarn\b",
    r"\bpnpm\b",
    r"\bgem\b",
    r"\bcargo\b",
    r"\bgo\b",
    r"\bcomposer\b",

    # Kernel modules
    r"\bmodprobe\b",
    r"\binsmod\b",
    r"\brmmod\b",
    r"\bdepmod\b",

    # Kernel parameters
    r"\bsysctl\b",

    # Filesystem & disk management
    r"\bmkfs\b",
    r"\bmkfs\.ext4\b",
    r"\bmkfs\.xfs\b",
    r"\bmkfs\.btrfs\b",
    r"\bmkfs\.vfat\b",
    r"\bmke2fs\b",
    r"\bfdisk\b",
    r"\bgdisk\b",
    r"\bparted\b",
    r"\bgparted\b",
    r"\btune2fs\b",
    r"\bresize2fs\b",
    r"\be2fsck\b",
    r"\bfsck\b",
    r"\bmount\b",
    r"\bumount\b",
    r"\bswapon\b",
    r"\bswapoff\b",
    r"\bmkswap\b",
    r"\blosetup\b",
    r"\bcryptsetup\b",
    r"\blvm\b",
    r"\bpvcreate\b",
    r"\bvgcreate\b",
    r"\blvcreate\b",
    r"\bpvremove\b",
    r"\bvgremove\b",
    r"\blvremove\b",

    # Network configuration
    r"\bip\b",
    r"\bifconfig\b",
    r"\biwconfig\b",
    r"\bnmcli\b",
    r"\bnmtui\b",
    r"\bnetplan\b",
    r"\bifup\b",
    r"\bifdown\b",
    r"\broute\b",
    r"\barp\b",
    r"\bethtool\b",

    # Firewall & packet filtering
    r"\biptables\b",
    r"\bip6tables\b",
    r"\bnft\b",
    r"\bufw\b",
    r"\bfirewall-cmd\b",
    r"\bipset\b",

    # Scheduling & automation
    r"\bcrontab\b",
    r"\bat\b",
    r"\bbatch\b",
    r"\bsystemd-run\b",
    r"\banacron\b",

    # Boot & bootloader
    r"\bgrub-install\b",
    r"\bgrub-mkconfig\b",
    r"\bupdate-grub\b",
    r"\bgrub2-install\b",
    r"\befibootmgr\b",
    r"\bbootctl\b",

    # System identity & time
    r"\bhostname\b",
    r"\bhostnamectl\b",
    r"\btimedatectl\b",
    r"\bdate\b",
    r"\bhwclock\b",
    r"\blocalectl\b",

    # Power & reboot
    r"\breboot\b",
    r"\bshutdown\b",
    r"\bpoweroff\b",
    r"\bhalt\b",

    # Dynamic linker / library cache
    r"\bldconfig\b",
    r"\bupdate-alternatives\b",
    r"\bdpkg-reconfigure\b",

    # Environment & resource limits
    r"\bulimit\b",
    r"\bprlimit\b",

    # Process & signal management
    r"\bkill\b",
    r"\bkillall\b",
    r"\bpkill\b",
    r"\bxkill\b",
    r"\brenice\b",
    r"\bionice\b",
    r"\bchrt\b",

    # Logging & audit manipulation (only destructive flags)
    r"\bjournalctl\b.*(--rotate|--vacuum)",
    r"\blogrotate\b",
    r"\bauditctl\b",

    # Pipe-to-shell: fetching and directly executing remote code.
    # Matches: curl ... | bash, wget ... | sh, wget ... | zsh, etc.
    r"\b(curl|wget|fetch)\b[^|#\n]*\|\s*(ba|da|z|fi)?sh\b",
    # Matches: bash <(curl ...) process substitution form
    r"\bbash\b\s+<\s*\(\s*(curl|wget)\b",
}


def _matches_any(tool_input: str, patterns: set) -> bool:
    return any(re.search(pattern, tool_input) for pattern in patterns)


def is_destructive(user_input, tool_input, intermediate_steps) -> bool:
    categories = [
        _DELETION_PATTERNS,
        _OVERWRITE_PATTERNS,
        _PERMISSION_PATTERNS,
        _SYSTEM_MUTATION_PATTERNS,
    ]
    return any(_matches_any(tool_input, patterns) for patterns in categories)