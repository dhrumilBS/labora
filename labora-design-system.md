# Labora Design System

**Version:** 1.0\
**Reference:** Supplied `labora-design-system.svg`\
**Purpose:** A reusable visual system for Labora website screens,
product UI, social posts, and marketing imagery.

------------------------------------------------------------------------

## 1. Brand Foundation

Labora uses a calm, nature-led visual language built around:

-   **Deep Teal** for authority, headlines, and dark backgrounds
-   **Labora Green** for actions, accents, buttons, icons, and the logo
    mark
-   **Mint** and **Cream** for generous visual space
-   **White** for cards and product UI surfaces
-   **Charcoal** for readable body copy

The overall design should feel **clean, calm, credible, modern, and
laboratory-focused**.

### Brand principle

> Green is the accent: use one primary green button, highlight, or icon
> set per layout.

------------------------------------------------------------------------

# 2. Logo

## Logo concept

The Labora mark is described as an **L that turns like a bench workflow,
with a dot representing the sample**.

### Logo rules

-   Never redraw the logo.
-   Never stretch or distort it.
-   Never recolor the approved logo artwork.
-   Maintain clear space around the logo.
-   Use the appropriate logo version for the background.

### Logo variants

  Variant          Recommended use
  ---------------- ---------------------------------------
  Primary          White, cream, or mint backgrounds
  Reversed         Deep Teal and dark photography
  On-brand-green   Small brand moments and stickers
  White mark       Approved dark-background applications

### Clear space

Keep empty space around the logo equal to **half the height of the mark
on every side**.

### Minimum size

-   **Mark:** 24 px tall minimum
-   **Full logo:** 96 px wide minimum
-   Below the full-logo minimum, use the **mark alone**

------------------------------------------------------------------------

# 3. Color

Labora's palette is built around deep teal, natural green, mint, cream,
and neutral surfaces.

## Core colors

  -----------------------------------------------------------------------
  Token             Hex               RGB               Primary use
  ----------------- ----------------- ----------------- -----------------
  Deep Teal         `#0D3A33`         13, 58, 51        Headlines, dark
                                                        backgrounds, logo
                                                        text

  Labora Green      `#11806A`         17, 128, 106      Primary accent,
                                                        buttons, icons,
                                                        logo mark

  Mint              `#DCF1E8`         220, 241, 232     Soft backgrounds
                                                        and
                                                        product-visual
                                                        shapes

  Cream             `#FBF8F1`         251, 248, 241     Light page and
                                                        social-post
                                                        backgrounds

  White             `#FFFFFF`         255, 255, 255     Cards and product
                                                        UI surfaces

  Charcoal          `#25302E`         37, 48, 46        Body text and
                                                        long paragraphs
  -----------------------------------------------------------------------

## Supporting colors

  -----------------------------------------------------------------------
  Token             Hex               RGB               Use
  ----------------- ----------------- ----------------- -----------------
  Teal 2            `#134A41`         19, 74, 65        Supporting dark
                                                        teal

  Green Dark        `#0B6654`         11, 102, 84       Dark green states

  Bright Green      `#2FB38F`         47, 179, 143      Dark-background
                                                        accent / CTA

  Light Green       `#8FE0C6`         143, 224, 198     Dark-background
                                                        icon and
                                                        highlight

  Chart Mint        `#B7E2D1`         183, 226, 209     Charts and data
                                                        visualization

  Mint Soft         `#EEF8F3`         238, 248, 243     Very light
                                                        product/UI
                                                        surfaces

  Muted Gray        `#56635F`         86, 99, 95        Secondary text

  Border            `#E0E6E2`         224, 230, 226     Standard borders

  Border Strong     `#CBD6D0`         203, 214, 208     Stronger borders
                                                        and controls
  -----------------------------------------------------------------------

## Status colors

Status colors are intended for **product UI only**.

  Status            Foreground   Background   Meaning
  ----------------- ------------ ------------ -------------
  Amber / Warning   `#B86E12`    `#FCF1E1`    Low stock
  Rose / Error      `#B4413C`    `#FBECEB`    Out of spec

## Color balance

The reference recommends approximately:

-   **60%** neutral space
-   **30%** Deep Teal
-   **10%** Labora Green

Use green as an accent rather than as a dominant fill.

------------------------------------------------------------------------

# 4. Accessibility & Contrast

Normal text should meet **4.5:1 WCAG AA contrast**.\
Large, bold text should meet **3:1**.

## Approved pairings

  Foreground / Background       Contrast Status
  --------------------------- ---------- ---------
  White on Deep Teal              12.6:1 AA pass
  White on Labora Green            4.9:1 AA pass
  Deep Teal on Mint               10.7:1 AA pass
  Charcoal on Cream               12.8:1 AA pass
  Light Green on Deep Teal         8.2:1 AA pass
  Deep Teal on Bright Green        4.8:1 AA pass

## Avoid

  Pairing                   Contrast Guidance
  ----------------------- ---------- ----------
  Bright Green on White        2.6:1 Avoid
  Light Green on White         1.5:1 Avoid

------------------------------------------------------------------------

# 5. Typography

## Typeface

**Mulish** is the primary typeface for the complete Labora system.

-   Source: Google Fonts
-   Fallback: `Segoe UI`, `Arial`
-   Available weights used by the system:
    -   Regular `400`
    -   SemiBold `600`
    -   Bold `700`
    -   ExtraBold `800`

### Typography principle

Hierarchy comes from **size and weight**, not from extra colors or
all-caps styling.

## Type scale

  Style             Size / Line height     Weight        Tracking
  ----------------- -------------------- -------- ---------------
  Display / H1      64 / 66 px                800           -3.5%
  H2 / Section      44 / 50 px                800             -3%
  H3 / Card title   22 / 28 px                700             -2%
  Body Large        20 / 32 px                400         Default
  Body              16 / 26 px                400         Default
  Label             14 / 20 px                700   Sentence case
  Caption           12.5 / 18 px              800         Default

### Typography examples

**H1**

> Run your lab smarter

**H2**

> Everything, connected

**H3**

> Know where every sample stands

**Body Large**

> Bring samples, inventory, and equipment together.

**Body**

> Every record is attributable, traceable, and protected.

**Label**

> Laboratory management software

**Caption**

> Updated 20 min ago

### Text rules

-   Use **sentence case**.
-   Do not use ALL CAPS for headlines.
-   Avoid adding colors simply to create hierarchy.
-   Use weight, size, spacing, and layout to establish hierarchy.

------------------------------------------------------------------------

# 6. Spacing, Radius & Elevation

## Spacing system

Labora follows an **8-point rhythm**.

### Spacing scale

``` text
4
8
12
16
24
32
48
64
```

### Layout guidance

-   Section padding: **96--128 px**
-   Standard card padding: **24 px**

Use the spacing scale consistently instead of introducing arbitrary
values.

## Corner radius

  Element                   Radius
  --------- ----------------------
  Small                      10 px
  Input                      14 px
  Card                       20 px
  Panel                      28 px
  Pill        Pill / fully rounded

## Elevation

Use only **two shadow levels**.

### UI card

Used for:

-   Cards
-   Product mockups
-   Standard elevated surfaces

### Floating

Used for:

-   Stat cards
-   Menus
-   Floating product elements

Avoid excessive shadows, glows, and glass effects.

------------------------------------------------------------------------

# 7. Components

Components are the reusable building blocks for the website, product
visuals, and marketing assets.

## Buttons

### Primary

-   One primary button per view where possible
-   Use **Labora Green**
-   Designed for the primary action

Example:

> Book a demo

### Secondary

-   Ghost button
-   Gray outline
-   Used for secondary actions

Example:

> Explore the platform

### On dark backgrounds

-   Use **Bright Green** as the fill
-   White outline where required by the design

### Button sizes

  Size       Height
  -------- --------
  Large       56 px
  Medium      48 px
  Small       40 px

------------------------------------------------------------------------

# 8. Badges & Tags

Use badges and tags for short product states, modules, and contextual
labels.

### Example states

-   Running
-   Available
-   Calibration
-   Out of spec

### Example labels

-   Laboratory information management
-   Laboratory management software

### Rule

Use **sentence case only**.

------------------------------------------------------------------------

# 9. Form Fields

Default field example:

``` text
Work email
name@lab.com
```

## States

### Default

Neutral border and standard surface.

### Focus

Use a **green + mint focus ring**.

### Validation

Example:

``` text
Work email
name@lab
Enter a valid work email.
```

Keep validation messages clear and close to the relevant field.

------------------------------------------------------------------------

# 10. Cards

Cards should feel lightweight, spacious, and product-oriented.

## Example: KPI card

``` text
Avg. turnaround
26.4 h
−1.8 h this week
```

## Example: Stat card

``` text
1,284
Active samples
```

## Example: Product module card

``` text
Inventory

Track reagents, lots, and expiry.

Explore solution
```

## Example: Equipment status card

``` text
Equipment status

HPLC-02          Running
Centrifuge C-4   Calibration
Balance B-7      Service
```

Use real product information or clearly illustrative UI. Do not invent
customer numbers, awards, certifications, or unsupported claims.

------------------------------------------------------------------------

# 11. Iconography

## Icon style

-   Outline icons
-   **24 × 24 px grid**
-   **1.8 px stroke**
-   Rounded ends
-   Labora Green on a Mint tile for the standard icon treatment

## Icon categories

The reference system includes icon concepts for:

-   Sample
-   Experiment
-   LIMS
-   ELN
-   Inventory
-   Workflow
-   Equipment
-   Quality
-   Analytics
-   Integrations
-   Automation
-   Visibility
-   Configure
-   Security
-   Audit trail
-   Insights

### Icon rule

Keep stroke weight and visual density consistent across the interface.
Avoid mixing filled, thin, and heavy icon styles within the same
component group.

------------------------------------------------------------------------

# 12. Social Post Templates

The system defines **three social layouts** for LinkedIn and Instagram.

### Export size

**1080 × 1080 px**

### Core rule

> Product UI is always the hero.

------------------------------------------------------------------------

## Template A --- Light

### Purpose

Announcements and product-value messages.

### Visual treatment

-   Cream background
-   Deep Teal headline
-   One green CTA
-   Product UI as the main visual

### Example structure

``` text
Labora

Laboratory management software

One platform to
manage your
entire laboratory

[Book a demo]

Lab overview

Received
146

Turnaround
26.4 h
```

------------------------------------------------------------------------

## Template B --- Dark

### Purpose

Features, security, and launches.

### Visual treatment

-   Deep Teal background
-   White headline
-   Light Green icons
-   Bright Green CTA
-   Product UI remains central

### Example structure

``` text
Labora

Know where
every sample
stands

Registration to report,
in one record.

[Learn more]
```

------------------------------------------------------------------------

## Template C --- Feature

### Purpose

Highlight one product module with one clear message.

### Visual treatment

-   Mint background
-   Module tag
-   One real product card
-   One feature/message

### Example structure

``` text
Labora

Inventory

Reorder before
experiments stall

Acetonitrile
Reorder

Serum, lot 4471
In stock

Trypsin T-88
Expiring
```

------------------------------------------------------------------------

# 13. Imagery & Product Visuals

## Preferred visual hierarchy

1.  Product UI / dashboard
2.  Relevant product card or data visualization
3.  Supporting brand elements
4.  Minimal decorative elements

The product interface should communicate the feature rather than being
treated as a small decorative screenshot.

## Recommended treatment

-   Use generous whitespace.
-   Keep UI surfaces crisp and readable.
-   Use Mint or Cream to create breathing room.
-   Use Deep Teal for authority.
-   Use green selectively for action and emphasis.
-   Prefer real product screens or the established mockup style.

## Avoid

-   Stock laboratory photos as the primary visual
-   Blue, purple, or rainbow gradients
-   Heavy glassmorphism
-   Multiple competing decorative effects
-   Excessive shadows or glows

------------------------------------------------------------------------

# 14. Do & Don't

## Do

-   Lead with product UI and dashboards.
-   Use one green accent per layout.
-   Leave generous whitespace.
-   Write headlines in sentence case.
-   Use real product screens or the established mockup style.
-   Keep claims factual and verifiable.
-   Maintain consistent spacing and corner radii.
-   Use the approved Labora palette.
-   Preserve accessibility contrast.
-   Keep the product UI as the hero in social graphics.

## Don't

-   Use stock lab photos as the main visual.
-   Add blue, purple, or rainbow gradients.
-   Put Bright Green or Light Green text on white.
-   Write headlines in ALL CAPS.
-   Stack many shadows, glows, or glass effects.
-   Invent customer numbers, awards, or certifications.
-   Redraw, stretch, or recolor the logo.
-   Introduce arbitrary colors without a documented system need.
-   Overcrowd layouts with decorative elements.

------------------------------------------------------------------------

# 15. Implementation Tokens

The following token structure can be used when translating the design
system into CSS or a frontend component library.

``` css
:root {
  /* Brand */
  --labora-deep-teal: #0D3A33;
  --labora-green: #11806A;
  --labora-mint: #DCF1E8;
  --labora-cream: #FBF8F1;
  --labora-white: #FFFFFF;
  --labora-charcoal: #25302E;

  /* Supporting */
  --labora-teal-2: #134A41;
  --labora-green-dark: #0B6654;
  --labora-bright-green: #2FB38F;
  --labora-light-green: #8FE0C6;
  --labora-chart-mint: #B7E2D1;
  --labora-mint-soft: #EEF8F3;
  --labora-muted-gray: #56635F;
  --labora-border: #E0E6E2;
  --labora-border-strong: #CBD6D0;

  /* Status */
  --labora-warning: #B86E12;
  --labora-warning-bg: #FCF1E1;
  --labora-error: #B4413C;
  --labora-error-bg: #FBECEB;

  /* Typography */
  --labora-font-family: "Mulish", "Segoe UI", Arial, sans-serif;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;

  /* Radius */
  --radius-small: 10px;
  --radius-input: 14px;
  --radius-card: 20px;
  --radius-panel: 28px;
  --radius-pill: 9999px;
}
```

------------------------------------------------------------------------

# 16. Design Checklist

Before delivering a Labora screen, graphic, or marketing asset, verify:

### Brand

-   [ ] Correct Labora logo variant
-   [ ] Logo has sufficient clear space
-   [ ] No logo distortion or recoloring

### Color

-   [ ] Palette uses approved Labora colors
-   [ ] Green is used as an accent
-   [ ] No unapproved blue, purple, or rainbow gradients
-   [ ] Text/background contrast is accessible

### Typography

-   [ ] Mulish is used
-   [ ] Correct hierarchy and weights
-   [ ] Headlines use sentence case
-   [ ] No unnecessary all-caps styling

### Layout

-   [ ] 8-point spacing rhythm
-   [ ] Generous whitespace
-   [ ] Consistent corner radii
-   [ ] Only the required elevation/shadow level

### Product UI

-   [ ] Product UI is clear and readable
-   [ ] Dashboard/card is treated as the hero where appropriate
-   [ ] Data and claims are factual
-   [ ] Status colors are reserved for product UI

### Marketing / Social

-   [ ] Correct 1080 × 1080 social format when applicable
-   [ ] One clear message
-   [ ] One green accent
-   [ ] Product UI remains the hero

------------------------------------------------------------------------

# 17. Reference Summary

  Area                    Labora standard
  ----------------------- -------------------------
  Primary font            Mulish
  Primary dark            `#0D3A33` Deep Teal
  Primary accent          `#11806A` Labora Green
  Main soft background    `#DCF1E8` Mint
  Main light background   `#FBF8F1` Cream
  Surface                 `#FFFFFF` White
  Body text               `#25302E` Charcoal
  Base spacing            8-point rhythm
  Section padding         96--128 px
  Card padding            24 px
  Card radius             20 px
  Panel radius            28 px
  Input radius            14 px
  Small radius            10 px
  Icon grid               24 px
  Icon stroke             1.8 px
  Social format           1080 × 1080 px
  H1                      64 / 66 px, ExtraBold
  H2                      44 / 50 px, ExtraBold
  H3                      22 / 28 px, Bold
  Body Large              20 / 32 px
  Body                    16 / 26 px
  Label                   14 / 20 px, Bold
  Caption                 12.5 / 18 px, ExtraBold

------------------------------------------------------------------------

**Labora Design System --- Version 1.0, 2026**

This document is derived from the supplied Labora design-system
reference and preserves its terminology, values, component guidance, and
visual rules.
