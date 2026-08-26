import AxeBuilder from "@axe-core/playwright";
import { expect, type Locator, test } from "@playwright/test";

const INSPECTOR_FIELDS = "Evidence ID|Source role|Source handle|Selector|Quoted span|Inspection level".split("|");
const STUDY_BLOCKS =
  "STUDY-DIRECT STUDY-TEXTS STUDY-GREEK STUDY-LEXICON STUDY-ALTERNATIVES STUDY-TEXTUAL-STATE STUDY-ASSESSMENT".split(
    " ",
  );

async function expectAllVisible(...locators: Locator[]) {
  for (const locator of locators) await expect(locator).toBeVisible();
}

async function expectVisibleFocus(control: Locator) {
  await expect(control).toBeFocused();
  const focus = await control.evaluate((node) => {
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    const center = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
    return {
      outline: style.outlineStyle,
      width: Number.parseFloat(style.outlineWidth),
      inViewport: rect.top >= 0 && rect.bottom <= innerHeight && rect.left >= 0 && rect.right <= innerWidth,
      unobscured: center === node || node.contains(center),
    };
  });
  expect(focus.outline).not.toBe("none");
  expect(focus.width).toBeGreaterThanOrEqual(3);
  expect(focus.inViewport).toBe(true);
  expect(focus.unobscured).toBe(true);
}

test.beforeEach(async ({ context, page }) => {
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== "http://127.0.0.1:4173") throw new Error(`non-loopback request: ${url.href}`);
    await route.continue();
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "John 1:5 Study workspace" })).toBeVisible();
});

test("semantic, keyboard, disclosure, and accessibility boundaries", async ({ page }) => {
  const headings = await page
    .locator("h1, h2, h3")
    .evaluateAll((nodes) => nodes.map((node) => Number(node.tagName[1])));
  expect(headings[0]).toBe(1);
  for (let index = 1; index < headings.length; index += 1)
    expect(headings[index] - headings[index - 1]).toBeLessThanOrEqual(1);
  await page.keyboard.press("Tab");
  const skip = page.getByRole("link", { name: "Skip to study content" });
  await expectVisibleFocus(skip);
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();

  const citationSummaries = page.locator(".disclosures summary");
  await expect(citationSummaries).toHaveCount(10);
  for (let index = 0; index < 10; index += 1) {
    const summary = citationSummaries.nth(index);
    await page.keyboard.press("Tab");
    await expectVisibleFocus(summary);
    await page.keyboard.press("Enter");
    const details = summary.locator("xpath=..");
    await expect(details).toHaveAttribute("open", "");
    await expect(details.locator("dt")).toHaveText(INSPECTOR_FIELDS);
    await expect(details.getByRole("heading", { name: "Linked claims" })).toBeVisible();
    await expectAllVisible(details.locator("dd").first(), details.locator("li").first());
    await expect(details.locator("li").first()).toContainText("Qualification:");
    await page.keyboard.press("Enter");
    await expect(details).not.toHaveAttribute("open", "");
  }

  await expect(page.getByText(/critical apparatus and witness evidence is absent/)).toBeVisible();
  await expect(page.getByText(/formal morphology does not by itself establish/)).toBeVisible();
  await expect(page.getByText(/conflict or defeat effect is strongly supported/)).toBeVisible();
  await expect(page.getByText("Ordered page-region alternative")).toBeVisible();
  expect(await page.locator("ol").filter({ hasText: "CANONICAL_TEXT" }).locator("li").count()).toBe(7);
  const audit = page.getByText(/Inspect deterministic publication identities/);
  await page.keyboard.press("Tab");
  await expectVisibleFocus(audit);
  await page.keyboard.press("Enter");
  await expect(page.getByText(/9f9f9dd44384d90/)).toBeVisible();
  const serious = (await new AxeBuilder({ page }).analyze()).violations.filter((item) =>
    ["serious", "critical"].includes(item.impact ?? ""),
  );
  expect(serious).toEqual([]);
  const hoverRules = await page.evaluate(() =>
    [...document.styleSheets].flatMap((sheet) => [...sheet.cssRules]).filter((rule) => rule.cssText.includes(":hover")),
  );
  expect(hoverRules).toEqual([]);
});

for (const width of [1280, 640, 390, 320]) {
  test(`reflows without horizontal page overflow at ${width} CSS pixels`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.reload();
    await expect(page.getByText(/not REV-P2 specialist gold/)).toBeVisible();
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(overflow).toBe(false);
    const columns = await page
      .locator(".translations")
      .evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length);
    expect(columns).toBe(width > 672 ? 2 : 1);
    await expect(page.locator("main section")).toHaveCount(9);
    await expect(page.locator("[data-block-id]")).toHaveCount(7);
    expect(
      await page.locator("[data-block-id]").evaluateAll((nodes) => nodes.map((node) => node.dataset.blockId)),
    ).toEqual(STUDY_BLOCKS);
    const translationComparison = page.getByRole("region", { name: "ASV and WEB Classic comparison" });
    const greek = page.getByRole("region", { name: "Greek and morphology" });
    const limits = page.getByRole("region", { name: "Textual-state limits and evidence horizon" });
    await expectAllVisible(
      page.getByRole("heading", { name: "American Standard Version" }),
      translationComparison.getByText("And the light shineth in the darkness; and the darkness apprehended it not.", {
        exact: true,
      }),
      translationComparison.getByText("apprehended it not", { exact: true }),
      page.getByRole("heading", { name: "World English Bible Classic" }),
      translationComparison.getByText("The light shines in the darkness, and the darkness hasn’t overcome it.", {
        exact: true,
      }),
      translationComparison.getByText("hasn’t overcome it", { exact: true }),
      greek.getByText("καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.", { exact: true }),
      greek.getByText("indicative · singular · third · aorist · active", { exact: true }),
      page.getByRole("region", { name: "Alternatives" }).getByText(/double resonance also remains plausible/),
      limits.getByText(/critical apparatus and witness evidence.*is absent/),
      limits.getByText(/historical English semantic evidence.*is absent/),
      page.getByAltText(/Legible BASE synthetic/),
      page.getByAltText(/DEGRADED_ILLEGIBILITY synthetic/),
      page.getByText(/Inspect deterministic publication identities/),
    );
    await expect(page.locator("ol").filter({ hasText: "CANONICAL_TEXT" }).locator("li")).toHaveCount(7);
    if (width === 320) {
      const serious = (await new AxeBuilder({ page }).analyze()).violations.filter((item) =>
        ["serious", "critical"].includes(item.impact ?? ""),
      );
      expect(serious).toEqual([]);
    }
  });
}

test("200-percent-equivalent reflow has no horizontal document overflow", async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.reload();
  await page.evaluate(() => {
    document.documentElement.style.zoom = "2";
  });
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(
    false,
  );
  await expect(page.locator("[data-block-id]")).toHaveCount(7);
  await expect(page.getByAltText(/DEGRADED_ILLEGIBILITY synthetic/)).toBeVisible();
});

test("reduced motion removes meaningful animation", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const duration = await page.locator("main").evaluate((node) => getComputedStyle(node).animationDuration);
  expect(["0.01ms", "0.00001s", "1e-05s"]).toContain(duration);
});
