## # FAQ Assistant Design Specification 

## ## Groww-Inspired Mutual Fund FAQ Assistant 

Version: 1.0 

--- 

## # Design Philosophy 

The UI should feel like a natural extension of Groww while clearly indicating: 

> "Prototype – Not affiliated with or supported by Groww." 

Design principles borrowed from Groww: 

- Large whitespace 

- Minimal typography 

- Green primary accent 

- Soft rounded cards 

- Trust-first layout 

- Clean illustrations 

- Mobile-first design 

- Single primary CTA 

- No clutter 

--- 

## # Brand Identity 

## Logo 

Use supplied logo: 

groww-app-icon-hd.png 

Placement: 

- Top left navbar 

- Login screen center 

- Loading screen animation 

--- 

## # Color Palette 

## Primary 

Groww Green 

```css #00D09C 

``` 

## ## Secondary 

```css #44475B ``` 

## Background 

```css #FFFFFF ``` 

## Dark Section 

```css #05070A ``` 

## Border 

```css 

#ECEFF3 ``` 

## ## Success 

```css 

#00D09C ``` 

## ## Error 

```css #FF4D4F ``` 

--- 

# Typography 

## Heading Inter Weight: 700 ## Body Inter 

Weight: 400 

## ## FAQ Answers 

Inter Weight: 500 --- 

## # User Flow 

```text Landing Page ↓ Login Page ↓ Welcome / Example Queries ↓ Chat Interface ↓ Answer ↓ Citation Link ``` 

--- 

# SCREEN 1 # Landing Page 

Inspired by Groww homepage hero section 

--- 

## ## Navbar 

-----------------------------------------------Logo 

FAQ Assistant 

About Features Sources 

Login Button 

------------------------------------------------ 

Login Button 

Background: #00D09C 

Text: White 

Radius: 999px 

--- 

## ## Hero Section 

Large illustration inspired by Groww city illustration. 

Suggested illustration: 

Financial knowledge hub 

Visual elements: 

- Documents 

- AMC Factsheets 

- Search nodes 

- AI assistant 

- Mutual fund cards 

--- 

### Hero Headline 

# Mutual Fund Facts, # Instantly Verified. 

--- 

### Hero Subheadline 

Get accurate information about mutual fund schemes using official AMC, SEBI and AMFI sources. 

No opinions. No investment advice. 

--- 

### Primary CTA 

Ask Fund Questions 

--- 

## ### Secondary CTA 

View Sources 

--- 

## ## Trust Banner 

━━━━━━━━━━━━━━━━━━━━━━━━━━ 

- ✓ Official Sources Only 

- ✓ AMC + SEBI + AMFI 

- ✓ Citation in Every Answer 

- ✓ No Investment Advice 

━━━━━━━━━━━━━━━━━━━━━━━━━━ 

--- 

## Feature Cards 

3 horizontal cards 

--- 

### Card 1 

Official Data 

Uses only AMC, SEBI and AMFI pages. 

--- 

### Card 2 

Fact Verification 

Every answer includes source links. 

--- 

### Card 3 

Safe & Compliant 

## Refuses buy/sell recommendations. 

--- 

## ## Example Questions 

Display in cards 

"What is the expense ratio of SBI Bluechip Fund?" 

"What is the lock-in period of SBI Long Term Equity Fund?" 

"How do I download my capital gains statement?" 

--- 

## Disclaimer Banner 

Background: Light Yellow 

⚠ Prototype only. Not affiliated with or supported by Groww. 

--- 

## # SCREEN 2 

# Login Screen 

Minimal Groww-inspired login 

--- 

## Layout 

Centered Card 

Width: 420px 

Radius: 24px 

Shadow: Soft 

--- 

## Logo 

## Centered 

Size: 72px 

--- 

## ## Heading 

Welcome Back 

--- 

## ## Subtext 

Access your Mutual Fund FAQ Assistant --- 

## Fields 

Email 

Password --- 

## Buttons Primary: 

Continue 

Green 

--- 

Secondary: Continue with Google 

Outlined 

--- 

Footer: 

Prototype Only No real investment transactions supported. 

--- 

## # SCREEN 3 

## # FAQ Assistant Chat 

Core Product Screen 

--- 

Background: #FAFBFC 

--- 

## ## Header 

------------------------------------------------ 

Logo 

Mutual Fund FAQ Assistant 

Facts Only 

------------------------------------------------ 

--- 

## ## Info Banner 

ℹ This assistant answers factual mutual fund questions. 

No investment advice. 

--- 

## ## Example Chips 

Expense Ratio 

Exit Load 

Minimum SIP 

Riskometer 

Benchmark 

Capital Gains Statement 

--- 

## # Chat Area 

--- 

## User Bubble 

Background: 

## #EAFBF6 

Radius: 20px 

--- 

Example 

What is the expense ratio of SBI Bluechip Fund? 

--- 

## Assistant Bubble 

White 

Border: #ECEFF3 

Radius: 20px 

--- 

Example Response 

Expense Ratio: 0.89% 

Source: SBI Mutual Fund Factsheet 

View Source → 

Last updated from sources: 29-May-2026 

--- 

## # Citation Card 

Always attached below answer 

-------------------------------- 

Source: SBI Mutual Fund 

Open Source → 

Last Updated: 29-May-2026 

-------------------------------- 

--- 

## # Refusal State 

If user asks: 

Should I invest in SBI Bluechip? 

--- 

## Assistant Response 

I can only provide factual information from official AMC, SEBI and AMFI sources. 

I cannot provide investment advice or recommendations. 

Learn more → 

--- 

## # Empty State 

Before first question 

Large illustration 

Heading: 

Ask Anything About Mutual Funds 

Subtext: 

Examples: 

- Expense ratio 

- Exit load 

- Benchmark 

- Riskometer 

- Lock-in period 

--- 

## # Loading State 

Logo animation 

Text: 

Searching official sources... 

--- 

## # Error State 

Could not find information in approved sources. 

Try rephrasing your question. 

--- 

## # Mobile Layout 

Priority: 

100% mobile responsive 

Breakpoints: 

```css Mobile: 0-768 Tablet: 768-1024 Desktop: 1024+ ``` 

--- 

# Component Library 

## Buttons 

### Primary 

Background: #00D09C 

Height: 48px Radius: 999px --### Secondary Border: 1px solid #ECEFF3 Background: White --## Cards Radius: 20px Padding: 24px Border: #ECEFF3 --## Chips Radius: 999px Padding: 12px 20px Background: #F6F7F9 --# Animation Guidelines Hero Illustration: Floating animation 

Duration: 4s --- 

FAQ Cards: 

Fade In 

Duration: 300ms --- 

Answer Card: 

Slide Up 

Duration: 250ms 

--- 

# Accessibility 

Minimum contrast: WCAG AA 

Keyboard navigation: Supported Screen reader labels: Required 

--- 

# Footer 

------------------------------------------------ 

Mutual Fund FAQ Assistant 

Official Sources Only 

AMC SEBI AMFI 

Facts Only • No Advice 

Prototype only. Not affiliated with or supported by Groww. 

------------------------------------------------ 

--- 

## # Final Experience 

User lands on: Landing Page 

↓ 

Clicks Login 

↓ 

Login Success 

↓ 

FAQ Chat 

↓ 

Ask Question 

↓ 

Receive Answer + Citation 

↓ 

Open Official Source 

↓ 

Trustworthy Fact Retrieval Experience 

