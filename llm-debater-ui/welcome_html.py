WELCOME_HTML = """
                    <div style='max-width: 900px; margin: 0 auto; padding: 32px; background-color: #ffffff; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); transition: all 0.3s ease;'>
                        <div style='text-align: center; margin-bottom: 40px;'>
                            <h2 style='font-size: 2.4em; color: #1a365d; font-weight: 600; letter-spacing: -0.5px;'>AI Debate Study: Participant Guidelines</h2>
                            <div style='width: 60px; height: 4px; background: linear-gradient(90deg, #2c5282, #4299e1); margin: 24px auto 0; border-radius: 2px;'></div>
                        </div>
                        
                        <div style='font-size: 1.2em; color: #2d3748;'>
                            <div class='section' style='margin-bottom: 32px;'>
                                <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>What Is This Study?</h3>
                                <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                    <p style='margin: 0; line-height: 1.6;'>This study examines how people interact with AI debaters when evaluating the factuality of statements or claims. You will engage in a three-round debates with two AI systems about a specific claim related to COVID-19.</p>
                                </div>
                            </div>

                            <div class='section' style='margin-bottom: 32px;'>
                                <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>How It Works</h3>
                                <div style='display: grid; gap: 16px;'>
                                    <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                        <p style='margin: 0 0 16px; font-weight: 500; color: #2d3748;'>Before You Begin:</p>
                                        <div style='display: grid; gap: 12px;'>
                                            <div style='display: flex; align-items: start; gap: 12px;'>
                                                <div style='min-width: 6px; height: 6px; background: #2c5282; border-radius: 3px; margin-top: 8px;'></div>
                                                <span>You'll be presented with a factual claim (which may be True or False)</span>
                                            </div>
                                            <div style='display: flex; align-items: start; gap: 12px;'>
                                                <div style='min-width: 6px; height: 6px; background: #2c5282; border-radius: 3px; margin-top: 8px;'></div>
                                                <span>There will be two AI debaters. Each debater will provide arguments about whether the claim is True or False. You must read each debater's arguments and follow the debate through all three rounds. At the end (after three rounds), you will make a final decision about whether the claim is True or False.</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                        <p style='margin: 0 0 16px; font-weight: 500; color: #2d3748;'>The Debate Process (3 Rounds):</p>
                                        <div style='display: grid; gap: 16px;'>
                                            <div style='padding: 16px; background: white; border-radius: 12px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                                <p style='font-weight: 500; margin: 0 0 8px;'>Round 1:</p>
                                                <ul style='margin: 0; padding-left: 20px;'>
                                                    <li>Read both AI debaters's initial arguments and evidence</li>
                                                    <li>Respond with questions, request clarifications, or share your thoughts (minimum 50 characters). You can address specific debaters by name (e.g., "Debater A, could you explain...?" or "Debater B, what evidence supports...?")</li>
                                                    <li>Click "Next Round" to proceed to Round 2</li>
                                                </ul>
                                            </div>
                                            <div style='padding: 16px; background: white; border-radius: 12px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                                <p style='font-weight: 500; margin: 0 0 8px;'>Round 2:</p>
                                                <ul style='margin: 0; padding-left: 20px;'>
                                                    <li>The AI debaters will address your questions, critique their opponent and provide additional arguments and evidence</li>
                                                    <li>Ask follow-up questions or request more information. Continue to address debaters by name when asking specific questions</li>
                                                    <li>Click "Next Round" to proceed to Round 3</li>
                                                </ul>
                                            </div>
                                            <div style='padding: 16px; background: white; border-radius: 12px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                                <p style='font-weight: 500; margin: 0 0 8px;'>Round 3:</p>
                                                <ul style='margin: 0; padding-left: 20px;'>
                                                    <li>The AI debaters will provide their final arguments and evidence</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class='section' style='margin-bottom: 32px;'>
                                <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>Your Final Judgment</h3>
                                <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                    <p style='margin: 0 0 16px;'>After the three debate rounds:</p>
                                    <ol style='margin: 0; padding-left: 20px;'>
                                        <li>Decide whether you believe the statement is True or False based on the evidence provided by each AI debater</li>
                                        <li>Indicate your confidence level (percentage slider)</li>
                                        <li>Explain your reasoning (minimum 50 characters) why you believe the statement is True or False</li>
                                        <li>Submit your final judgment and return to Prolific to track your completion</li>
                                    </ol>
                                </div>
                            </div>

                        <div class='section' style='margin-bottom: 32px;'>
                            <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>Tips for Effective Debate</h3>
                            <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                <ul style='margin: 0; padding-left: 20px;'>
                                    <li>Address debaters by their designated names (Debater A or Debater B) when directing questions</li>
                                    <li>Ask for specific details about arguments and evidence presented (e.g., "Debater A, could you explain this evidence in more detail?")</li>
                                    <li>Question the reliability of sources (e.g., "Debater B, how reliable is this particular source?")</li>
                                    <li>Request clarification on ambiguous points (e.g., "Can you explain what you mean by this point?")</li>
                                    <li>Challenge potential weaknesses in the debater's argument (e.g., "What are the potential limitations of this analysis?")</li>
                                </ul>
                            </div>
                        </div>

                            <div style='text-align: center; color: #718096; margin-top: 32px; padding-top: 24px; border-top: 1px solid #e2e8f0;'>
                                Your responses will be collected anonymously and used for research purposes by the MARS Lab at UCLA.
                            </div>
                        </div>
                    </div>

                    <div style='max-width: 900px; margin: 20px auto; padding: 24px; background-color: #f8fafc; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8); transition: all 0.3s ease;'>
                        <div style='display: flex; align-items: center; justify-content: center; gap: 12px;'>
                            <div style='font-size: 1.1em; color: #2d3748;'>
                                Proceeding means you have read and understood the debate guidelines
                            </div>
                        </div>
                    </div>
            """

TERMS_HTML = """
                            <div class="max-w-2xl mx-auto p-6 bg-white rounded-xl">
                                <h2 class="text-2xl font-bold text-center mb-6">Terms and Conditions</h2>
                                
                                <div class="space-y-6 text-gray-700">
                                    <p class="text-center text-lg", style="font-size: 1.3em;">Welcome to this AI debate platform, a research initiative by the MARS Lab at UCLA. Here, you'll engage in interactive debate with advanced AI language model. By participating, you agree to provide evaluative feedback as a judge and complete all debate sessions. We prioritize your privacy and do not collect any personally identifiable information.</p>
                                </div>
                            </div>
                        """

LLM_EXPERIENCE_HTML = """
                    <div style='font-size: 1.2em; margin: 1.5rem 0; line-height: 1.6;'>
                        Before we begin, please indicate your level of experience with AI assistants like ChatGPT, Claude, or Bard.
                        
                        NOTE: Your answer has no effect on your compensation or how we view your responses. We value your honest feedback, regardless of your experience level. Your compensation is guaranteed as long as you properly complete all required sessions.
                    </div>
                """