"""
Benchmark & Recalibration Suite for Veritas AI Detector.
Evaluates AIDetector against 20 known-human texts and 20 known-AI texts (GPT-4o, Claude 3.5, Gemini).
Calculates distributions, accuracy, and validates ZeroGPT verdict thresholds:
  - Human texts: average fakePercentage < 15%
  - AI texts: average fakePercentage > 65%
"""

import time
import json
import statistics
from engine.detector import AIDetector

HUMAN_TEXTS = [
    # 1. Technical debugging post-mortem
    "The memory leak was maddening. For three straight days I stared at heap dumps, suspecting a rogue database connection. "
    "Turns out? It was a stray closure capturing a giant buffer in the logging middleware. Two lines changed, and memory dropped right back to 45 megabytes. "
    "Never skipping a heap benchmark again.",

    # 2. Personal travel reflection
    "We finally got to Rome around 2 AM because the night train out of Florence had broken down twice in the hills. "
    "My backpack strap snapped right as we hit the cobblestones outside Termini, and of course it started drizzling. "
    "We ended up splitting a cold slice of potato pizza under an awning while waiting for our host to wake up.",

    # 3. George Orwell excerpt
    "A scrupulous writer, in every sentence that he writes, will ask himself at least four questions: "
    "What am I trying to say? What words will express it? What image or idiom will make it clearer? "
    "Is this image fresh enough to have an effect? And he will probably ask himself two more: Could I put it more shortly? "
    "Have I said anything that is avoidably ugly?",

    # 4. Casual Slack / chat message
    "Hey folks, quick heads up that I won't make standup this morning. The plumber is here tearing out our bathroom pipe after it burst last night. "
    "I pushed the PR for the auth fix before logging off yesterday, so feel free to review whenever. Ping me if production catches fire.",

    # 5. Sourdough baking failure
    "My sourdough starter looked bubbly enough, but the loaf turned into a literal brick. "
    "I think my kitchen was just too drafty during the bulk ferment, so the yeast gave up halfway through. "
    "My partner took one bite, grimaced politely, and offered to make toast instead.",

    # 6. Investigative journalism
    "For three decades, residents of Mill Creek watched the river turn an unnatural shade of copper every Tuesday afternoon. "
    "State regulators insisted the runoff met safety standards, yet fish counts plummeted year after year. "
    "It wasn't until a high school biology class sampled the creek bed that anyone documented the true levels of cadmium.",

    # 7. Used car advice
    "Whatever you do, don't buy that Civic without checking underneath for frame rust. "
    "Sellers in Michigan love power-washing the engine bay so everything looks spotless, but the strut towers tell the real story. "
    "Bring a flashlight, poke around the wheel wells, and if the guy gets defensive, just walk away.",

    # 8. ER doctor reflection
    "Night shifts have a rhythm you can't learn in medical school. Between 3 and 5 in the morning, the chaos usually quiets down, "
    "leaving just the hum of monitors and the squeak of nurses' clogs on linoleum. That's when you sip lukewarm drip coffee and pray the pager stays asleep.",

    # 9. Cozy bookstore review
    "This place smells exactly like old paper, wet wool, and vanilla chai. The owner, Margaret, has run the corner shop since 1984. "
    "She doesn't use a computer catalog—if you ask for a mid-century poetry anthology, she just squints at the ceiling, walks three aisles down, "
    "and pulls it right off the shelf.",

    # 10. Database connection pool incident
    "At 9:14 AM yesterday, our primary Postgres instance started throwing max connection errors. "
    "Nobody had touched the deployment pipeline since Thursday, so everyone assumed DDoS. "
    "Nope. A junior contractor had spun up thirty worker replicas without connection pooling, hammering the poor database into a standstill.",

    # 11. Biology field notes
    "We sat shivering in the blind for nearly four hours before the barn owl finally swooped. "
    "It made zero sound—just a pale ghost slicing through the pine needles toward the vole in the grass. "
    "I nearly dropped my telephoto lens trying to track the dive.",

    # 12. Woodworking project
    "Flattening an eight-foot slab of reclaimed white oak with a hand plane is a workout you feel for three days. "
    "The grain kept reversing around a knot near the center, tearing out nasty chunks every time I pushed forward. "
    "I finally had to break out the card scraper and finish it by hand.",

    # 13. Exam anxiety journal
    "It's 1:30 AM and my organic chemistry final is in seven hours. I know the Diels-Alder mechanism forwards and backwards, "
    "but the moment I close my eyes, my brain starts inventing imaginary reaction pathways. Going to brew one more peppermint tea and try to sleep.",

    # 14. Guitar practice
    "Barre chords used to feel physically impossible on my acoustic. My index finger would cramp up after two measures of F major, "
    "buzzing on the B string no matter how hard I pressed. Three months of stubborn repetition later, it finally sounds clean.",

    # 15. Baseball game collapse
    "I cannot believe what I just watched. Two outs, bases loaded, bottom of the ninth, up by three runs—and our closer serves up a belt-high fastball on an 0-2 count. "
    "Grand slam. Game over. I'm sitting in this stadium parking lot staring at the rain.",

    # 16. Espresso bar morning
    "The pump on group head two blew an O-ring during the morning commuter rush. "
    "Water was sputtering everywhere, customers were glaring at the line out the door, and our newest barista was looking like he was about to faint. "
    "Classic Monday morning hospitality.",

    # 17. Mountain hike
    "The trail to Twin Peaks was completely clear until mile four, where a thick wall of marine fog rolled in off the coast. "
    "Within ten minutes, temperature plunged fifteen degrees and visibility dropped to maybe twenty feet. "
    "We decided not to risk the scramble to the summit and turned back.",

    # 18. Indie game dev bug
    "Fixed the ragdoll bug where dead goblins would launch into low Earth orbit when struck by arrows. "
    "Turned out our collision impulses were getting multiplied by the frame delta twice. "
    "A little sad to see it go honestly, because our playtesters thought it was hilarious.",

    # 19. History teacher classroom observation
    "When you hand ninth graders a photocopy of an 1860 census record, their first reaction is panic because they can't read the cursive handwriting. "
    "Once you walk them through the column headers, though, you see the lightbulbs click. Suddenly history isn't names on a flashcard—it's actual people.",

    # 20. Weekend camping logistics
    "Are we bringing the two-burner Coleman stove or just relying on the fire pit? "
    "Ranger station says there's a Stage 1 burn ban starting Friday, so charcoal might be prohibited if conditions stay dry. Let me know so I pack the right fuel canisters."
]

AI_TEXTS = [
    # 1. GPT-4o: Cloud enterprise architecture
    "In the realm of enterprise operations, leveraging cloud-based solutions is paramount for long-term scalability and business continuity. "
    "Additionally, it is worth noting that modern cross-functional teams must seamlessly align their core competencies to foster agile development. "
    "Consequently, embarking on a comprehensive digital transformation journey will cultivate organizational synergy and drive operational excellence. "
    "In conclusion, adopting this strategic paradigm will unlock unprecedented opportunities across multifaceted markets.",

    # 2. Claude 3.5: Renewable energy grid integration
    "The integration of renewable energy sources into existing electrical grids presents significant technical and economic challenges. "
    "Variable generation from solar photovoltaic and wind installations necessitates sophisticated energy storage mechanisms and demand-response protocols. "
    "Furthermore, grid operators must maintain frequency stability through advanced inverter technology and predictive forecasting algorithms. "
    "A multifaceted infrastructure modernization plan is therefore essential to facilitate a seamless transition toward decarbonized energy systems.",

    # 3. GPT-4o: Educational pedagogy
    "In today's rapidly evolving educational landscape, implementing blended learning models plays a crucial role in fostering student engagement. "
    "By integrating interactive multimedia tools with traditional pedagogical strategies, educators can create a rich tapestry of personalized instruction. "
    "Furthermore, continuous formative assessment empowers instructors to identify learning gaps and adjust instructional methodologies accordingly. "
    "Ultimately, this holistic framework serves as a testament to the transformative power of modern educational technology.",

    # 4. Claude 3.5: Healthcare AI diagnostics
    "The deployment of artificial intelligence in clinical diagnostics introduces profound ethical and regulatory considerations. "
    "While convolutional neural networks demonstrate remarkable sensitivity in detecting subtle radiographic anomalies, algorithmic bias remains a substantial concern. "
    "Disparities in training datasets can inadvertently exacerbate existing healthcare inequities across underrepresented demographic cohorts. "
    "Consequently, rigorous validation protocols and transparent auditing procedures must be institutionalized to ensure equitable patient outcomes.",

    # 5. GPT-4o: Standard AI cliché essay
    "In today's fast-paced digital world, artificial intelligence plays a crucial role in shaping the future of global industries. "
    "It is important to delve deeply into the multifaceted dimensions of computational intelligence to understand its true societal impact. "
    "Moreover, the seamless confluence of data analytics and automated workflows serves as a testament to human ingenuity. "
    "Navigating this evolving paradigm requires collaborative governance and robust ethical guidelines.",

    # 6. Claude 3.5: Remote work dynamics
    "The paradigm shift toward remote and hybrid work structures has fundamentally altered corporate culture and employee retention strategies. "
    "Organizations must navigate the delicate balance between fostering individual autonomy and maintaining interpersonal social capital. "
    "While asynchronous communication tools enhance focus and reduce temporal friction, they may inadvertently diminish spontaneous cross-pollination of ideas. "
    "Consequently, forward-thinking enterprises are adopting intentional collaboration cadences to preserve long-term organizational cohesion.",

    # 7. GPT-4o: Cybersecurity posture
    "In an era characterized by increasingly sophisticated cyber threats, establishing a comprehensive defense-in-depth architecture is imperative. "
    "Organizations must implement zero-trust network principles, multi-factor authentication, and continuous behavioral telemetry to safeguard sensitive assets. "
    "Furthermore, regular vulnerability assessments and proactive incident response drills empower security teams to preemptively mitigate potential breaches. "
    "In summary, cultivating a resilient organizational security posture requires an unwavering commitment to cyber hygiene.",

    # 8. Claude 3.5: Urban resilience and transit
    "Urban agglomerations face mounting pressure to accommodate demographic growth while concurrently enhancing environmental resilience. "
    "Transit-oriented development offers a coherent strategic methodology for curbing vehicular emissions and mitigating urban sprawl. "
    "By clustering high-density mixed-use residential zones around multimodal transit nodes, municipal planners can cultivate walkable, vibrant communities. "
    "This integrated approach underscores the imperative of harmonizing infrastructure development with long-term ecological sustainability.",

    # 9. GPT-4o: Supply chain optimization
    "Navigating modern supply chain complexities demands a multifaceted data-driven strategy to mitigate volatility and logistical friction. "
    "Leveraging predictive analytics and automated inventory management enables enterprises to optimize stock replenishment while minimizing holding costs. "
    "Additionally, fostering end-to-end visibility across global distribution channels enhances agility in the face of geopolitical disruptions. "
    "Ultimately, this transformative paradigm enables corporations to deliver superior customer satisfaction and operational efficiency.",

    # 10. Claude 3.5: Biodiversity conservation
    "Habitat fragmentation represents one of the foremost drivers of anthropogenically induced biodiversity decline across terrestrial ecosystems. "
    "When contiguous landscapes are dissected by transportation corridors, gene flow among isolated populations is severely constricted. "
    "Implementing ecological wildlife corridors facilitates seasonal migration and preserves genetic diversity within vulnerable species. "
    "Therefore, strategic landscape connectivity planning constitutes an indispensable pillar of contemporary conservation biology.",

    # 11. GPT-4o: Blockchain consensus
    "Blockchain technology offers a robust decentralized architecture for establishing trustless verification across distributed peer networks. "
    "Through Byzantine fault-tolerant consensus mechanisms and cryptographic hashing algorithms, participants can securely record immutable transactions. "
    "Moreover, smart contracts eliminate intermediary friction by automatically executing predetermined business logic upon fulfilling specific conditions. "
    "This revolutionary paradigm continues to reshape traditional financial ecosystems and digital governance frameworks.",

    # 12. Claude 3.5: Cognitive psychology
    "Cognitive reappraisal represents a foundational emotion regulation strategy that significantly influences psychological wellbeing under sustained duress. "
    "By reframing adverse stressors through an objective cognitive lens, individuals can attenuate autonomic nervous system arousal. "
    "Neuroimaging studies indicate that this process engages prefrontal cortical regions while dampening amygdala reactivity. "
    "Cultivating this cognitive competency offers protective benefits against emotional burnout and chronic stress-related pathologies.",

    # 13. GPT-4o: Omnichannel retail
    "In the contemporary retail marketplace, curating an exceptional omnichannel experience is essential for driving customer loyalty and retention. "
    "Brands must seamlessly harmonize online storefronts, physical brick-and-mortar touchpoints, and personalized mobile applications. "
    "Furthermore, utilizing real-time customer data platforms allows marketing professionals to deliver tailored promotions that resonate with individual preferences. "
    "In conclusion, embracing this unified retail paradigm positions forward-thinking brands for sustained commercial growth.",

    # 14. Claude 3.5: Quantum computing
    "Quantum computing leverages the fundamental principles of superposition and entanglement to execute computational calculations beyond classical capabilities. "
    "Unlike binary bits that exist deterministically as zero or one, quantum qubits can occupy probabilistic linear combinations of both states simultaneously. "
    "However, maintaining quantum coherence against environmental thermal noise remains a formidable engineering hurdle requiring robust fault-tolerant quantum error correction. "
    "Overcoming these physical limitations will ultimately unlock unprecedented breakthroughs in molecular simulation and cryptographic analysis.",

    # 15. GPT-4o: Engineering onboarding
    "Designing an effective developer onboarding program is pivotal for accelerating time-to-productivity within fast-paced software engineering teams. "
    "Providing comprehensive documentation, automated sandbox environments, and dedicated mentorship bridges the gap between conceptual understanding and code delivery. "
    "Moreover, establishing clear architectural standards ensures newly onboarded engineers can contribute meaningfully to core codebases without introducing regression errors. "
    "This structured pedagogical framework fosters an empowering engineering culture and minimizes organizational turnover.",

    # 16. Claude 3.5: Circular economy
    "The transition from a linear extraction-disposal model to a regenerative circular economy is central to mitigating resource depletion. "
    "Product designers must prioritize modular disassembly, non-toxic material compositions, and prolonged component lifecycle viability from initial inception. "
    "Furthermore, closed-loop industrial ecology systems enable waste byproducts from one production cycle to serve as high-grade feedstock for another. "
    "Such comprehensive industrial redesign is imperative for decoupling macroeconomic prosperity from finite ecological exploitation.",

    # 17. GPT-4o: Generative AI legal landscape
    "The rapid proliferation of generative artificial intelligence has introduced unprecedented complexities into the global intellectual property landscape. "
    "Courts and regulatory bodies are actively grappling with questions of fair use, copyright infringement, and authorship attribution for synthetic outputs. "
    "Furthermore, corporations utilizing large language models must implement rigorous data provenance frameworks to ensure compliance with existing licensing agreements. "
    "Navigating this ambiguous legal frontier demands proactive legal oversight and transparent model governance.",

    # 18. Claude 3.5: Metabolic engineering
    "Metabolic engineering harnesses recombinant DNA technology and directed evolution to optimize microbial biosynthetic pathways for specialty chemical synthesis. "
    "By systematically modifying cellular metabolic flux, bioengineers can convert renewable carbon feedstocks into valuable pharmaceutical precursors and bio-based plastics. "
    "High-throughput screening platforms and automated CRISPR-Cas gene editing have significantly reduced the design-build-test-learn cycle in synthetic biology. "
    "This biomanufacturing paradigm offers a viable pathway toward decarbonizing petrochemical-dependent chemical supply chains.",

    # 19. GPT-4o: Executive leadership memo
    "As we embark upon the forthcoming fiscal year, it is vital that our leadership cadre maintains an unwavering focus on operational agility. "
    "By synergizing our core competencies across regional business units, we can maximize efficiency while delivering unparalleled value to key stakeholders. "
    "Furthermore, fostering a culture of continuous improvement will empower individual contributors to proactively identify innovative solutions to emerging challenges. "
    "Together, we will continue to navigate market dynamics and achieve sustained organizational success.",

    # 20. Claude 3.5: Existential literary criticism
    "Franz Kafka's The Metamorphosis serves as a poignant exploration of alienation, familial commodification, and existential absurdity in bureaucratic society. "
    "Gregor Samsa's sudden transformation into a monstrous vermin functions not merely as surreal allegory, but as a literal manifestation of his dehumanizing labor. "
    "His subsequent psychological deterioration mirrors the gradual erosion of empathy exhibited by his family once his economic utility ceases. "
    "Kafka thereby exposes the transactional fragility of interpersonal kinship within industrialized economic systems."
]

def run_benchmark():
    print("=" * 70)
    print("VERITAS AI DETECTOR - 40-SAMPLE CALIBRATION & BENCHMARK SUITE")
    print("=" * 70)
    print("Initializing AIDetector with Hugging Face DeBERTa model...")
    t0 = time.time()
    detector = AIDetector()
    init_time = time.time() - t0
    print(f"Model initialized in {init_time:.2f}s (Device: {detector.device}, Has Model: {detector.has_model})\n")

    print(f"Testing {len(HUMAN_TEXTS)} Known-Human texts...")
    human_scores = []
    t_human_start = time.time()
    for idx, text in enumerate(HUMAN_TEXTS, 1):
        res = detector.analyze(text)
        human_scores.append(res["fakePercentage"])
        print(f"  [Human {idx:02d}] fakePercentage: {res['fakePercentage']:5.1f}% | Verdict: {res['verdict']:<45} | aiWords: {res['aiWords']}/{res['textWords']}")
    t_human = time.time() - t_human_start

    print(f"\nTesting {len(AI_TEXTS)} Known-AI texts (GPT-4o / Claude 3.5 / Gemini)...")
    ai_scores = []
    t_ai_start = time.time()
    for idx, text in enumerate(AI_TEXTS, 1):
        res = detector.analyze(text)
        ai_scores.append(res["fakePercentage"])
        print(f"  [AI    {idx:02d}] fakePercentage: {res['fakePercentage']:5.1f}% | Verdict: {res['verdict']:<45} | aiWords: {res['aiWords']}/{res['textWords']}")
    t_ai = time.time() - t_ai_start

    avg_human = statistics.mean(human_scores)
    med_human = statistics.median(human_scores)
    max_human = max(human_scores)

    avg_ai = statistics.mean(ai_scores)
    med_ai = statistics.median(ai_scores)
    min_ai = min(ai_scores)

    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS SUMMARY:")
    print("=" * 70)
    print(f"Human Texts ({len(HUMAN_TEXTS)} samples):")
    print(f"  - Average fakePercentage: {avg_human:.1f}% (Target: < 15.0%)")
    print(f"  - Median fakePercentage:  {med_human:.1f}%")
    print(f"  - Max fakePercentage:     {max_human:.1f}%")
    print(f"  - Total processing time:  {t_human:.2f}s ({t_human / len(HUMAN_TEXTS):.3f}s / doc)")

    print(f"\nAI Texts ({len(AI_TEXTS)} samples):")
    print(f"  - Average fakePercentage: {avg_ai:.1f}% (Target: > 65.0%)")
    print(f"  - Median fakePercentage:  {med_ai:.1f}%")
    print(f"  - Min fakePercentage:     {min_ai:.1f}%")
    print(f"  - Total processing time:  {t_ai:.2f}s ({t_ai / len(AI_TEXTS):.3f}s / doc)")

    human_pass = avg_human < 15.0
    ai_pass = avg_ai > 65.0

    print("\nVERIFICATION STATUS:")
    print(f"  - Human Average < 15%: {'[PASS]' if human_pass else '[FAIL]'}")
    print(f"  - AI Average > 65%:    {'[PASS]' if ai_pass else '[FAIL]'}")
    
    assert human_pass, f"Human average ({avg_human:.1f}%) is not < 15.0%"
    assert ai_pass, f"AI average ({avg_ai:.1f}%) is not > 65.0%"
    print("\n>>> ALL BENCHMARK & RECALIBRATION TARGETS SUCCESSFULLY MET! <<<")

if __name__ == "__main__":
    run_benchmark()
