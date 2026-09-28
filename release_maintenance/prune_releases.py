"""Release-only repository maintenance. Never imported by the desktop app.

Keep the three highest numeric versions (including historical prereleases).
Delete release records/assets only; never tags, commits or local app files.
Default is a read-only plan. --apply is reserved for the repository workflow.
"""
import argparse
import json
import os
import re
import urllib.request

REPOSITORY = "animochoi-2026/FineDiaryMessenger"
ASSET = "FineDiaryMessenger-windows-x64.zip"
KEEP = 3


def version(tag):
    if not isinstance(tag, str) or not re.fullmatch(r"v?\d+(?:\.\d+){0,2}", tag):
        return None
    parts = tuple(int(part) for part in tag.lstrip("v").split("."))
    return parts + (0,) * (3 - len(parts))


def uploaded_package(release):
    prefix = f"https://github.com/{REPOSITORY}/releases/download/{release['tag_name']}/"
    assets = release.get("assets", [])
    for name in (ASSET, ASSET + ".sha256"):
        matches = [asset for asset in assets if asset.get("name") == name]
        if len(matches) != 1:
            return False
        asset = matches[0]
        if (asset.get("state") != "uploaded" or not asset.get("size", 0) > 0
                or asset.get("browser_download_url") != prefix + name):
            return False
        if name == ASSET and not re.fullmatch(r"sha256:[a-fA-F0-9]{64}", asset.get("digest") or ""):
            return False
    return True


def retention_plan(releases):
    """Fail closed: an incomplete retained release cannot evict a good one."""
    releases = [r for r in releases if not r.get("draft") and version(r.get("tag_name")) is not None]
    releases.sort(key=lambda r: version(r["tag_name"]), reverse=True)
    versions = [version(r["tag_name"]) for r in releases]
    ids = [r["id"] for r in releases]
    if len(set(versions)) != len(versions) or len(set(ids)) != len(ids):
        raise ValueError("Duplicate version or release ID; nothing deleted")
    if any(type(ident) is not int or ident <= 0 for ident in ids):
        raise ValueError("Invalid release ID; nothing deleted")
    keep, remove = releases[:KEEP], releases[KEEP:]
    if remove and not all(uploaded_package(r) for r in keep):
        raise ValueError("Retained packages are not fully uploaded/verified; nothing deleted")
    return keep, remove


class GitHub:
    def __init__(self, token=""):
        self.token = token

    def request(self, suffix, method="GET"):
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "FineDiary-release-retention"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = urllib.request.Request(
            f"https://api.github.com/repos/{REPOSITORY}/{suffix}", headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response) if method == "GET" else None

    def releases(self):
        result = []
        for page in range(1, 101):
            batch = self.request(f"releases?per_page=100&page={page}")
            if not isinstance(batch, list):
                raise ValueError("Invalid release response; nothing deleted")
            result.extend(batch)
            if len(batch) < 100:
                return result
        raise ValueError("Release pagination limit reached; nothing deleted")

    def delete(self, release_id):
        self.request(f"releases/{release_id}", "DELETE")


def prune(api, apply=False):
    keep, remove = retention_plan(api.releases())
    print("KEEP:", ", ".join(r["tag_name"] for r in keep) or "none")
    print("DELETE" if apply else "WOULD DELETE", ", ".join(r["tag_name"] for r in remove) or "none")
    if not apply:
        return keep, remove
    keep_ids = [r["id"] for r in keep]
    expected_remove = [r["id"] for r in remove]
    for release in remove:
        # Recheck before every mutation. A concurrent publish/edit/upload
        # must not allow a stale plan to remove a newly protected version.
        fresh_keep, fresh_remove = retention_plan(api.releases())
        if ([r["id"] for r in fresh_keep] != keep_ids
                or [r["id"] for r in fresh_remove] != expected_remove
                or next(r for r in fresh_remove if r["id"] == release["id"])["tag_name"] != release["tag_name"]):
            raise ValueError("Release list changed during cleanup; stopped")
        api.delete(release["id"])
        expected_remove.remove(release["id"])
        print("DELETED:", release["tag_name"], "(release and assets; tag retained)")
    final_keep, final_remove = retention_plan(api.releases())
    if final_remove or [r["id"] for r in final_keep] != keep_ids:
        raise ValueError("Post-cleanup verification failed; inspect repository")
    return keep, remove


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if os.environ.get("GITHUB_REPOSITORY", REPOSITORY) != REPOSITORY:
        raise ValueError("Refusing to run for another repository")
    token = os.environ.get("GH_TOKEN", "")
    if args.apply and not token:
        raise ValueError("--apply requires the repository workflow token")
    prune(GitHub(token), apply=args.apply)


if __name__ == "__main__":
    main()
