import json
import os
import re
import unittest

from _load import ROOT, SKILLS_DIR

SKILLS = ["pmf", "pmf-pressure", "pmf-research", "pmf-panel", "pmf-offer",
          "pmf-numbers", "pmf-test", "pmf-build", "pmf-marketing", "pmf-brand",
          "pmf-ops", "pmf-launch", "pmf-plan"]

ABOUT = ("Thirteen product-market fit skills that take a business from idea to launch in "
         "Claude Code, Codex and OpenCode: an adversarial pressure test, real market "
         "research, a simulated buyer panel, the offer and its price, unit economics, "
         "a real-world demand test with pre-set criteria, the smallest MVP with agentic "
         "coding discipline, marketing, brand, operations, the launch and the compiled plan.")

BANNED = ("$ARGUMENTS", "CLAUDE_", "claude_skill_dir", "\u2014")

TOOLS = {"pmf": ["status.py"],
         "pmf-panel": ["panel.py"],
         "pmf-offer": ["van_westendorp.py"],
         "pmf-numbers": ["unit_economics.py"],
         "pmf-test": ["experiments.py"],
         "pmf-plan": ["compile.py"]}


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


def text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", ".reference", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".py", ".json", ".sh", ".yml", ".csv")) or f in ("LICENSE", ".gitignore"):
                yield os.path.join(base, f)


class RepoStructure(unittest.TestCase):
    def test_thirteen_skill_folders(self):
        found = sorted(d for d in os.listdir(SKILLS_DIR)
                       if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertIn("description: ", fm, s)
            self.assertGreater(len(fm), 200, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 40, s)

    def test_skills_are_harness_neutral(self):
        for path in text_files():
            if not path.startswith(SKILLS_DIR + os.sep) or not path.endswith(".md"):
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for token in BANNED:
                self.assertNotIn(token, text, "%s contains %r" % (path, token))
            if os.path.basename(path) == "SKILL.md" or "references" in path.split(os.sep):
                self.assertIn("pmf/", text, "%s never mentions the state contract" % path)

    def test_skills_point_to_their_next_step(self):
        for s in SKILLS:
            with open(os.path.join(SKILLS_DIR, s, "SKILL.md"), encoding="utf-8") as fh:
                self.assertIn("Next:", fh.read(), s)

    def test_local_skill_links_resolve(self):
        for path in text_files():
            if not path.startswith(SKILLS_DIR + os.sep) or not path.endswith(".md"):
                continue
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
                if "://" in target or target.startswith("#"):
                    continue
                linked = os.path.normpath(os.path.join(os.path.dirname(path), target))
                self.assertTrue(linked.startswith(SKILLS_DIR + os.sep), linked)
                self.assertTrue(os.path.isfile(linked), "%s links to %s" % (path, target))

    def test_research_bundles_its_platform_routes(self):
        research = os.path.join(SKILLS_DIR, "pmf-research")
        with open(os.path.join(research, "SKILL.md"), encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("[references/reach.md](references/reach.md)", body)
        self.assertIn("pmf/research/reach.md", body)
        with open(os.path.join(research, "references", "reach.md"), encoding="utf-8") as fh:
            routes = fh.read()
        for platform in ("Web search", "Web pages", "RSS", "GitHub", "Twitter/X",
                         "Reddit", "XiaoHongShu", "Facebook", "Instagram", "V2EX",
                         "YouTube", "Bilibili", "Xiaoyuzhou", "LinkedIn",
                         "Boss Zhipin", "Xueqiu"):
            self.assertIn("| " + platform, routes, platform)
        for name in ("web.md", "communities.md", "video.md", "business.md"):
            self.assertIn("(%s)" % name, routes)

    def test_tools_live_in_their_skill_folder(self):
        for skill, names in TOOLS.items():
            for name in names:
                self.assertTrue(os.path.isfile(os.path.join(SKILLS_DIR, skill, name)),
                                "%s/%s missing" % (skill, name))

    def test_no_em_dashes_or_non_ascii(self):
        for path in text_files():
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            self.assertTrue(all(ord(c) < 128 for c in body),
                            "%s contains non-ASCII characters" % os.path.relpath(path, ROOT))


class Manifests(unittest.TestCase):
    def test_claude_plugin_manifests(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "pmf")
        self.assertEqual(plugin["license"], "MIT")
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["name"], "pmf")
        self.assertEqual(market["plugins"][0]["name"], "pmf")
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_codex_plugin_manifest(self):
        with open(os.path.join(ROOT, ".codex-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "pmf")
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertEqual(plugin["license"], "MIT")

    def test_versions_agree(self):
        versions = []
        for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            with open(os.path.join(ROOT, rel)) as fh:
                versions.append(json.load(fh)["version"])
        self.assertEqual(len(set(versions)), 1)

    def test_repository_urls_and_display_name(self):
        url = "https://github.com/Rish-it/pmf"
        for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            with open(os.path.join(ROOT, rel)) as fh:
                plugin = json.load(fh)
            self.assertEqual(plugin["homepage"], url)
            self.assertEqual(plugin["repository"], url)
            self.assertEqual(plugin["description"], ABOUT)
            if "interface" in plugin:
                self.assertEqual(plugin["interface"]["displayName"], "PMF")
                self.assertEqual(plugin["interface"]["websiteURL"], url)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["plugins"][0]["homepage"], url)


class Readme(unittest.TestCase):
    def test_readme_contract(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# pmf:"))
        for line in (
            ABOUT,
            "## Install",
            "/plugin marketplace add Rish-it/pmf",
            "codex plugin marketplace add Rish-it/pmf",
            "install.sh",
            "## Research access",
            "pmf/research/reach.md",
            "## Fine print",
            "MIT",
        ):
            self.assertIn(line, readme, line)
        for s in SKILLS:
            self.assertIn("`skills/%s`" % s, readme)


if __name__ == "__main__":
    unittest.main()
