WELCOME_HTML = """
                <div style='max-width: 900px; margin: 0 auto; padding: 32px; background-color: #ffffff; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); transition: all 0.3s ease;'>
                    <div style='text-align: center; margin-bottom: 40px;'>
                        <h2 style='font-size: 2.4em; color: #1a365d; font-weight: 600; letter-spacing: -0.5px;'>AI Consultancy Study: Participant Guidelines</h2>
                        <div style='width: 60px; height: 4px; background: linear-gradient(90deg, #2c5282, #4299e1); margin: 24px auto 0; border-radius: 2px;'></div>
                    </div>
                    
                    <div style='font-size: 1.2em; color: #2d3748;'>
                        <div class='section' style='margin-bottom: 32px;'>
                            <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>What Is This Study?</h3>
                            <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                <p style='margin: 0; line-height: 1.6;'>This study examines how people interact with AI consultants when evaluating the factuality of statements or claims. You will engage in a three-round consultation with an AI system about a specific claim related to COVID-19.</p>
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
                                            <span>You'll be presented with a factual claim (which may be TRUE or FALSE)</span>
                                        </div>
                                        <div style='display: flex; align-items: start; gap: 12px;'>
                                            <div style='min-width: 6px; height: 6px; background: #2c5282; border-radius: 3px; margin-top: 8px;'></div>
                                            <span>The AI consultant will be assigned to argue that this statement is either TRUE or FALSE</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                    <p style='margin: 0 0 16px; font-weight: 500; color: #2d3748;'>The Consultation Process (3 Rounds):</p>
                                    <div style='display: grid; gap: 16px;'>
                                        <div style='padding: 16px; background: white; border-radius: 12px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                            <p style='font-weight: 500; margin: 0 0 8px;'>Round 1:</p>
                                            <ul style='margin: 0; padding-left: 20px;'>
                                                <li>Read the AI consultant's initial arguments and evidence</li>
                                                <li>Respond with questions, request clarifications, or share your thoughts (minimum 50 characters)</li>
                                                <li>Click "Submit Response" to proceed to Round 2</li>
                                            </ul>
                                        </div>
                                        <div style='padding: 16px; background: white; border-radius: 12px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                            <p style='font-weight: 500; margin: 0 0 8px;'>Round 2:</p>
                                            <ul style='margin: 0; padding-left: 20px;'>
                                                <li>The AI consultant will address your questions and provide additional arguments and evidence</li>
                                                <li>Ask follow-up questions or request more information</li>
                                                <li>Click "Submit Response" to proceed to Round 3</li>
                                            </ul>
                                        </div>
                                        <div style='padding: 16px; background: white; border-radius: 12px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                            <p style='font-weight: 500; margin: 0 0 8px;'>Round 3:</p>
                                            <ul style='margin: 0; padding-left: 20px;'>
                                                <li>The AI consultant will provide final arguments and evidence</li>
                                                <li>Submit your final response</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class='section' style='margin-bottom: 32px;'>
                            <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>Your Final Judgment</h3>
                            <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                                <p style='margin: 0 0 16px;'>After the three consultation rounds:</p>
                                <ol style='margin: 0; padding-left: 20px;'>
                                    <li>Decide whether you believe the statement is TRUE or FALSE based on the evidence provided by the AI consultant</li>
                                    <li>Indicate your confidence level (percentage slider)</li>
                                    <li>Explain your reasoning (minimum 50 characters) why you believe the statement is TRUE or FALSE</li>
                                    <li>Submit your final judgment and return to Prolific to track your completion</li>
                                </ol>
                            </div>
                        </div>

                    <div class='section' style='margin-bottom: 32px;'>
                        <h3 style='font-size: 1.5em; color: #2c5282; margin-bottom: 16px; font-weight: 500;'>Tips for Effective Consultation</h3>
                        <div style='background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.8);'>
                            <ul style='margin: 0; padding-left: 20px;'>
                                <li>Ask for specific details about arguments and evidence presented (e.g., "Could you explain this evidence in more detail?")</li>
                                <li>Question the reliability of sources (e.g., "How reliable is this particular source?")</li>
                                <li>Request clarification on ambiguous points (e.g., "Can you explain what you mean by this point?")</li>
                                <li>Challenge potential weaknesses in the consultant's argument (e.g., "What are the potential limitations of this analysis?")</li>
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
                        <input type='checkbox' 
                            id='guidelines-check' 
                            style='
                                transform: scale(1.2); 
                                margin-right: 12px;
                                accent-color: #2c5282;
                                -webkit-appearance: none;
                                -moz-appearance: none;
                                appearance: none;
                                width: 20px;
                                height: 20px;
                                border: 2px solid #2c5282;
                                border-radius: 6px;
                                cursor: pointer;
                                position: relative;
                                background-color: white;
                                transition: all 0.2s ease;
                            '
                            onchange="
                                this.style.backgroundColor = this.checked ? '#2c5282' : 'white';
                                document.getElementById('start-debate-btn').style.opacity = this.checked ? '1' : '0.5';
                                document.getElementById('start-debate-btn').style.cursor = this.checked ? 'pointer' : 'not-allowed';
                                document.getElementById('start-debate-btn').disabled = !this.checked;
                            ">
                        <div style='font-size: 1.1em; color: #2d3748;'>
                            I have read and understood the consultation guidelines
                        </div>
                    </div>
                </div>
        """


TERMS_AND_CONDITIONS_HTML = """
                            <div class="max-w-2xl mx-auto p-6 bg-white rounded-xl">
                                <h2 class="text-2xl font-bold text-center mb-6">Terms and Conditions</h2>
                                
                                <div class="space-y-6 text-gray-700">
                                    <p class="text-center text-lg", style="font-size: 1.3em;">Welcome to this AI consultancy platform, a research initiative by the MARS Lab at UCLA. Here, you'll engage in interactive consultations with an advanced AI language model. By participating, you agree to provide evaluative feedback as a judge and complete all consultation sessions. We prioritize your privacy and do not collect any personally identifiable information.</p>
                                </div>
                            </div>
                        """