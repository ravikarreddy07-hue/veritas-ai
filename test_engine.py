"""Automated test suite verifying that AI text is detected and humanized under 20% AI likelihood."""
from engine.detector import AIDetector
from engine.humanizer import AIHumanizer

def test_under_20_percent():
    detector = AIDetector()
    humanizer = AIHumanizer()

    # 1. Standard ChatGPT Output
    ai_sample = (
        "In today's fast-paced digital world, artificial intelligence plays a crucial role in modern society. "
        "Furthermore, it is important to note that machine learning algorithms foster innovation across multifaceted industries. "
        "A rich tapestry of computational tools serves as a testament to human ingenuity. "
        "Moreover, navigating the complexities of data science requires a holistic approach to succeed."
    )

    r_ai = detector.analyze(ai_sample)
    print("AI Sample Analysis:")
    print(f"  Initial AI %: {r_ai['ai_percentage']}%")
    print(f"  Verdict: {r_ai['verdict']}")
    assert r_ai['ai_percentage'] >= 65, f"Expected AI >= 65%, got {r_ai['ai_percentage']}%"

    # 2. Humanize in Aggressive / Stealth mode
    h_agg = humanizer.humanize(ai_sample, tone="natural", intensity="aggressive")
    r_agg = detector.analyze(h_agg['humanized_text'])
    print("\nAggressive Humanization Output:")
    print(f"  Text: {h_agg['humanized_text']}")
    print(f"  AI %: {r_agg['ai_percentage']}%")
    print(f"  Verdict: {r_agg['verdict']}")
    assert r_agg['ai_percentage'] < 20, f"Expected AI < 20%, but got {r_agg['ai_percentage']}%"

    # 3. Humanize in Balanced mode
    h_bal = humanizer.humanize(ai_sample, tone="natural", intensity="balanced")
    r_bal = detector.analyze(h_bal['humanized_text'])
    print("\nBalanced Humanization Output:")
    print(f"  Text: {h_bal['humanized_text']}")
    print(f"  AI %: {r_bal['ai_percentage']}%")
    print(f"  Verdict: {r_bal['verdict']}")
    assert r_bal['ai_percentage'] < 20, f"Expected AI < 20%, but got {r_bal['ai_percentage']}%"

    # 4. Corporate AI Sample
    corp_ai = (
        "In the realm of enterprise operations, leveraging cloud-based solutions is paramount for long-term scalability. "
        "Additionally, it is worth noting that modern cross-functional teams must seamlessly align their core competencies. "
        "Consequently, embarking on a digital transformation journey will foster synergy and drive operational excellence. "
        "In conclusion, adopting this strategic paradigm will unlock unprecedented opportunities."
    )
    r_corp_init = detector.analyze(corp_ai)
    h_corp = humanizer.humanize(corp_ai, tone="professional", intensity="aggressive")
    r_corp_done = detector.analyze(h_corp['humanized_text'])
    print("\nCorporate AI Humanization:")
    print(f"  Initial AI %: {r_corp_init['ai_percentage']}%")
    print(f"  Humanized AI %: {r_corp_done['ai_percentage']}%")
    print(f"  Verdict: {r_corp_done['verdict']}")
    assert r_corp_done['ai_percentage'] < 20, f"Expected Corporate Humanized AI < 20%, got {r_corp_done['ai_percentage']}%"

    print("\nSUCCESS: ALL HUMANIZED OUTPUTS ARE VERIFIED UNDER 20% AI SCORE!")

if __name__ == "__main__":
    test_under_20_percent()
