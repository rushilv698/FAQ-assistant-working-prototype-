"""Approved source registry for the MF facts assistant (HDFC, Kotak, SBI, Nippon + AMFI/SEBI)."""

SOURCE_LIST = [
    # ── HDFC Mutual Fund — core & investor services ──────────────────────────
    ("https://www.hdfcfund.com", "web"),
    ("https://www.hdfcfund.com/investor-services", "web"),
    ("https://www.hdfcfund.com/services/forms", "web"),
    ("https://www.hdfcfund.com/services/consolidated-account-statement", "web"),
    ("https://www.hdfcfund.com/investor-services/request-statement", "web"),
    ("https://www.hdfcfund.com/learn/blog/how-get-capital-gain-statement-mutual-fund-schemes-india", "web"),
    ("https://www.hdfcfund.com/investor-services/fund-documents", "web"),
    ("https://www.hdfcfund.com/investor-services/fund-documents/kim", "web"),
    ("https://www.hdfcfund.com/investor-services/fund-documents/sid", "web"),
    ("https://www.hdfcfund.com/investor-services/fund-documents/scheme-summary", "web"),
    # HDFC — scheme pages (direct plans)
    ("https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct", "web"),
    ("https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct", "web"),
    ("https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct", "web"),
    ("https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct", "web"),
    # HDFC — scheme pages (regular plans)
    ("https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/regular", "web"),
    ("https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/regular", "web"),
    ("https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/regular", "web"),
    ("https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/regular", "web"),
    # HDFC — FAQs, education, statutory
    ("https://www.hdfcfund.com/services/faqs/introduction-direct-plan", "web"),
    ("https://www.hdfcfund.com/services/faqs/systematic-investment-plan", "web"),
    ("https://www.hdfcfund.com/services/faqs/redemption-related-faqs", "web"),
    ("https://www.hdfcfund.com/learn/blog/direct-plans-vs-regular-plans", "web"),
    ("https://www.hdfcfund.com/learn/blog/mutual-fund-fees-and-charges-india", "web"),
    ("https://www.hdfcfund.com/learn/blog/key-terms-concepts", "web"),
    ("https://www.hdfcfund.com/statutory-disclosure/methodology-calculating-sale-repurchase-price", "web"),

    # ── Kotak Mutual Fund ────────────────────────────────────────────────────
    ("https://www.kotakmf.com", "web"),
    ("https://www.kotakmf.com/Scheme/Kotak-Flexi-Cap-Fund", "web"),
    ("https://www.kotakmf.com/Scheme/Kotak-ELSS-Tax-Saver-Fund", "web"),
    ("https://www.kotakmf.com/Scheme/Kotak-Bluechip-Fund", "web"),
    ("https://www.kotakmf.com/Scheme/Kotak-Balanced-Advantage-Fund", "web"),
    ("https://www.kotakmf.com/Knowledge-Center/FAQs", "web"),

    # ── SBI Mutual Fund ──────────────────────────────────────────────────────
    ("https://www.sbimf.com", "web"),
    ("https://www.sbimf.com/en-us/schemes/equity-schemes/sbi-bluechip-fund", "web"),
    ("https://www.sbimf.com/en-us/schemes/equity-schemes/sbi-long-term-equity-fund", "web"),
    ("https://www.sbimf.com/en-us/schemes/equity-schemes/sbi-flexicap-fund", "web"),
    ("https://www.sbimf.com/en-us/schemes/hybrid-schemes/sbi-balanced-advantage-fund", "web"),
    ("https://www.sbimf.com/en-us/investor-services/faqs", "web"),

    # ── Nippon India Mutual Fund ─────────────────────────────────────────────
    ("https://mf.nipponindiaim.com", "web"),
    ("https://mf.nipponindiaim.com/nippon-india-large-cap-fund", "web"),
    ("https://mf.nipponindiaim.com/nippon-india-tax-saver-elss-fund", "web"),
    ("https://mf.nipponindiaim.com/nippon-india-flexi-cap-fund", "web"),
    ("https://mf.nipponindiaim.com/nippon-india-balanced-advantage-fund", "web"),
    ("https://mf.nipponindiaim.com/investor-education/faq", "web"),

    # ── AMFI — investor education ────────────────────────────────────────────
    ("https://www.amfiindia.com/kyc", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=MythsAndFactsAboutMutualFunds", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=CutOffTimingsAndNewRuleOnApplicableNAV", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=DirectPlan", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=SIP", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=ExitLoad", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=Riskometer", "web"),
    ("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=ExpenseRatio", "web"),

    # ── SEBI — investor education ────────────────────────────────────────────
    ("https://investor.sebi.gov.in/understanding_mf.html", "web"),
    ("https://investor.sebi.gov.in/regular_and_direct_mutual_funds.html", "web"),
    ("https://investor.sebi.gov.in/kyc.html", "web"),
    ("https://investor.sebi.gov.in/consolidated_account_statement.html", "web"),
    ("https://investor.sebi.gov.in/elss.html", "web"),
    ("https://investor.sebi.gov.in/sip.html", "web"),
    ("https://investor.sebi.gov.in/expense_ratio.html", "web"),
]
