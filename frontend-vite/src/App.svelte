<script>
  import { onMount } from 'svelte';
  
  let currentStep = 1;
  let formData = {
    idea: '',
    plan: '',
    roadmap: '',
    currency: 'USD'
  };
  let isLoading = false;
  let result = null;
  let error = null;
  let showLoadingScreen = false;
  let currentMessage = '';
  let showResults = false;
  
  const questions = [
    { id: 1, text: "What's your software idea?", placeholder: "Describe your software idea..." },
    { id: 2, text: "What's your implementation plan?", placeholder: "How do you plan to build it?" },
    { id: 3, text: "What's your go-to-market strategy?", placeholder: "How will you launch and grow?" }
  ];

  const loadingMessages = [
    "Unleashing the power of AI to evaluate your vision...",
    "Analyzing market potential and innovation factors...",
    "Crunching numbers and calculating your valuation...",
    "Your idea is being evaluated with cutting-edge algorithms...",
    "Great ideas take time - we're making it count!"
  ];

  const consultingMessages = [
    'Consulting industry advisors...',
    'Contacting VC funds...',
    'Analyzing market potential...',
    'Finalizing valuation...'
  ];

  function nextStep() {
    if (currentStep < 3) {
      currentStep++;
    } else {
      submitForm();
    }
  }

  function prevStep() {
    if (currentStep > 1) currentStep--;
  }

  function getRandomMessage() {
    return loadingMessages[Math.floor(Math.random() * loadingMessages.length)];
  }

  async function showLoadingSequence() {
    showLoadingScreen = true;
    
    for (const message of consultingMessages) {
      currentMessage = message;
      // Change message every 2 seconds
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Additional delay after last message
    await new Promise(resolve => setTimeout(resolve, 1000));
    showLoadingScreen = false;
  }

  async function submitForm() {
    if (!formData.idea || !formData.plan) return;
    
    isLoading = true;
    error = null;
    showResults = true; // Always show results view
    currentStep = 4; // Skip to results
    
    // Show loading sequence
    await showLoadingSequence();
    
    try {
      const response = await fetch('/api/evaluate/idea', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          idea: formData.idea,
          plan: formData.plan,
          roadmap: formData.roadmap || 'Not provided',
          currency: formData.currency
        })
      });
      
      if (!response.ok) throw new Error('Network response was not ok');
      result = await response.json();
    } catch (err) {
      // Create a failure result
      result = {
        error: true,
        message: 'Request failed. Please try again later.',
        evaluation_summary: 'We encountered an error while processing your request.'
      };
      console.error('Error:', err);
    } finally {
      isLoading = false;
    }
  }

  function resetForm() {
    currentStep = 1;
    formData = {
      idea: '',
      plan: '',
      roadmap: '',
      currency: 'USD'
    };
    result = null;
    error = null;
  }
</script>

<main class="app-container">
  <header>
    <h1>The Max Appraiser</h1>
    <p class="tagline">Know your true value</p>
  </header>

  <div class="progress-container">
    <div class="progress-track">
      <div class="progress-fill" style={`width: ${((currentStep - 1) / 3) * 100}%`}></div>
    </div>
    <div class="steps">
      {#each [1, 2, 3] as step}
        <div class="step {currentStep >= step ? 'active' : ''}">
          <span class="step-number">{step}</span>
        </div>
      {/each}
      <div class="step {currentStep >= 4 ? 'active' : ''}">
        <span class="step-number">E</span>
      </div>
    </div>
  </div>
  
  <footer class="app-footer">
    <p>A MaxOSL Creation</p>
  </footer>

  {#if showLoadingScreen}
    <div class="loading-screen">
      <div class="loading-content">
        <div class="spinner"></div>
        <h2>Evaluating Your Software...</h2>
        <p class="loading-message">{currentMessage}</p>
      </div>
    </div>
  {:else if currentStep <= 3}
    <div class="form-container">
      {#if currentStep === 1}
        <div class="question">
          <label for="idea">What's your software idea?</label>
          <textarea
            id="idea"
            bind:value={formData.idea}
            placeholder="Describe your software idea..."
            rows="5"
          ></textarea>
        </div>
      {:else if currentStep === 2}
        <div class="question">
          <label for="plan">What's your implementation plan?</label>
          <textarea
            id="plan"
            bind:value={formData.plan}
            placeholder="How do you plan to build it?"
            rows="5"
          ></textarea>
        </div>
      {:else if currentStep === 3}
        <div class="question">
          <label for="roadmap">What's your go-to-market strategy?</label>
          <textarea
            id="roadmap"
            bind:value={formData.roadmap}
            placeholder="How will you launch and grow?"
            rows="5"
          ></textarea>
          <div class="currency-selector">
            <label for="currency">Currency:</label>
            <select id="currency" bind:value={formData.currency}>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="JPY">JPY (¥)</option>
            </select>
          </div>
        </div>
      {/if}

      <div class="form-actions">
        {#if currentStep > 1}
          <button on:click={prevStep} class="btn btn-secondary">Back</button>
        {:else}
          <div></div> <!-- Empty div for spacing -->
        {/if}
        <button 
          on:click={nextStep}
          disabled={isLoading || (currentStep === 1 && !formData.idea) || (currentStep === 2 && !formData.plan) || (currentStep === 3 && !formData.roadmap)}
          class="primary"
        >
          {currentStep === 3 ? 'Get Valuation' : 'Next'}
          {#if isLoading}
            <span class="spinner"></span>
          {/if}
        </button>
      </div>
    </div>

  {:else if showResults}
    <div class="results-container {result?.error ? 'error' : ''}">
      {#if result?.error}
        <div class="error-message">
          <h2>Evaluation Failed</h2>
          <p>{result.message}</p>
          <p>{result.evaluation_summary}</p>
          <button class="btn primary" on:click={() => {
            currentStep = 1;
            formData = { idea: '', plan: '', roadmap: '', currency: 'USD' };
            result = null;
            showResults = false;
          }}>
            Try Again
          </button>
        </div>
      {:else if result}
        <div>
          <h2>Your Evaluation Results</h2>
          <div class="grade-container">
            <div class="grade">{result.grade}</div>
            <div class="score">Overall Score: {(result.scores.overall * 100).toFixed(0)}/100</div>
          </div>
          <div class="scores-grid">
            <div class="score-item">
              <div class="score-label">Originality</div>
              <div class="score-bar">
                <div class="score-fill" style="width: {result.scores.originality * 100}%"></div>
                <span class="score-value">{(result.scores.originality * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <div class="score-item">
              <div class="score-label">Feasibility</div>
              <div class="score-bar">
                <div class="score-fill" style="width: {result.scores.feasibility * 100}%"></div>
                <span class="score-value">{(result.scores.feasibility * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <div class="score-item">
              <div class="score-label">Market Need</div>
              <div class="score-bar">
                <div class="score-fill" style="width: {result.scores.market_need * 100}%"></div>
                <span class="score-value">{(result.scores.market_need * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <div class="score-item">
              <div class="score-label">Competitive Edge</div>
              <div class="score-bar">
                <div class="score-fill" style="width: {result.scores.competitive_edge * 100}%"></div>
                <span class="score-value">{(result.scores.competitive_edge * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
          
          <div class="valuation">
            <h3>Estimated Valuation</h3>
            <div class="valuation-amount">
              {new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: result.valuation.currency || 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
              }).format(result.valuation.amount)}
            </div>
          </div>
          
          <div class="evaluation-details">
            <div class="detail-section">
              <h3>Strengths</h3>
              <ul>
                {#each result.strengths as strength}
                  <li>{strength}</li>
                {/each}
              </ul>
            </div>
            
            <div class="detail-section">
              <h3>Potential Risks</h3>
              <ul>
                {#each result.risks as risk}
                  <li>{risk}</li>
                {/each}
              </ul>
            </div>
            
            <div class="detail-section full-width">
              <h3>Recommendations</h3>
              <ul class="recommendations">
                {#each result.recommendations as rec}
                  <li>{rec}</li>
                {/each}
              </ul>
            </div>
            
            <div class="detail-section full-width">
              <h3>Evaluation Summary</h3>
              <p>{result.evaluation_summary}</p>
            </div>
            
            {#if result.market_analysis?.keywords?.market_terms?.length > 0}
              <div class="detail-section">
                <h3>Market Keywords</h3>
                <div class="keyword-tags">
                  {#each result.market_analysis.keywords.market_terms as keyword}
                    <span class="keyword-tag">{keyword}</span>
                  {/each}
                </div>
              </div>
            {/if}
            
            {#if result.market_analysis?.keywords?.tech_terms?.length > 0}
              <div class="detail-section">
                <h3>Tech Keywords</h3>
                <div class="keyword-tags">
                  {#each result.market_analysis.keywords.tech_terms as keyword}
                    <span class="keyword-tag">{keyword}</span>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          
          <div class="motivational-message">
            <p>✨ Remember: Your idea is what you make it. This evaluation is just the beginning. ✨</p>
          </div>
          
          <button class="btn primary" on:click={() => {
            currentStep = 1;
            formData = { idea: '', plan: '', roadmap: '', currency: 'USD' };
            result = null;
            showResults = false;
          }}>
            Start New Evaluation
          </button>
        </div>
      {/if}
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-overlay">
      <div class="spinner"></div>
      <p class="loading-message">{currentMessage}</p>
      <p class="loading-subtext">This usually takes 10-15 seconds</p>
    </div>
  {/if}

  {#if error}
    <div class="error">{error}</div>
  {/if}
</main>

<style>
  :root {
    --primary: #1a1a1a;
    --primary-dark: #000000;
    --text: #2d2d2d;
    --text-light: #666666;
    --border: #e0e0e0;
    --bg: #ffffff;
    --radius: 8px;
    --shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    --font-heading: 'Playfair Display', Georgia, serif;
    --font-body: 'Source Serif Pro', Georgia, serif;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :global(html), :global(body) {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }

  :global(body) {
    font-family: var(--font-body);
    line-height: 1.7;
    color: var(--text);
    background-color: #ffffff;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .app-container {
    flex: 1;
    width: 100%;
    max-width: 1000px;
    margin: 0 auto;
    padding: 4rem 3rem;
    background: var(--bg);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    box-sizing: border-box;
    gap: 2.5rem;
  }

  h1 {
    font-family: var(--font-heading);
    font-size: 3.5rem;
    margin: 0 0 0.5rem;
    color: var(--text);
    font-weight: 600;
    letter-spacing: -0.5px;
    line-height: 1.1;
  }

  .tagline {
    color: var(--text-light);
    margin: 0;
    font-size: 1.5rem;
    font-family: var(--font-heading);
    font-weight: 400;
    font-style: italic;
    letter-spacing: 0.5px;
    position: relative;
    display: inline-block;
  }

  .tagline::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
  }

  .progress-container {
    width: 100%;
    max-width: 700px;
    margin: 0 auto 2rem;
    position: relative;
    padding: 0 30px;
  }

  .progress-track {
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    position: absolute;
    top: 23px;
    left: 25px;
    right: 25px;
    z-index: 1;
  }

  .progress-fill {
    height: 100%;
    background: var(--primary);
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .steps {
    display: flex;
    justify-content: space-between;
    position: relative;
    z-index: 2;
    gap: 10px;
    padding: 0 10px;
  }

  .step {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: white;
    border: 2px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-light);
    font-weight: 700;
    font-size: 1.2rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    position: relative;
  }

  .step.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
    transform: scale(1.1);
  }

  .form-container {
    margin: 2rem 0;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .app-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    padding: 1rem 0;
    background: white;
    color: var(--text-muted);
    font-size: 0.9rem;
    border-top: 1px solid var(--border);
    z-index: 1000;
  }
  
  .loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .loading-content {
    text-align: center;
    max-width: 500px;
    padding: 2rem;
  }
  
  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid var(--border);
    border-top: 4px solid var(--primary);
    border-radius: 50%;
    margin: 0 auto 2rem;
    animation: spin 1s linear infinite;
  }
  
  .loading-message {
    margin-top: 1.5rem;
    font-size: 1.2rem;
    color: var(--text);
    min-height: 2rem;
  }
  
  .loading-subtext {
    color: var(--text-light);
    font-size: 1rem;
    margin-top: -1rem;
    font-style: italic;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .question {
    margin-bottom: 3rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    max-width: 800px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
  }

  label {
    display: block;
    margin-bottom: 0.75rem;
    font-weight: 600;
    color: var(--text);
    font-size: 1.3rem;
    letter-spacing: -0.2px;
  }

  textarea, select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-size: 1rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
  }

  textarea:focus, select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
  }

  label[for] {
    cursor: pointer;
  }

  textarea {
    min-height: 180px;
    resize: none;
    font-size: 1.2rem;
    line-height: 1.7;
    padding: 1.5rem;
    border: 2px solid #eee;
    border-radius: 8px;
    transition: all 0.3s ease;
    flex: 1;
    width: 100%;
    box-sizing: border-box;
  }

  textarea:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
  }

  button {
    padding: 1rem 2rem;
    border: none;
    border-radius: 4px;
    font-weight: 500;
    font-family: var(--font-body);
    letter-spacing: 0.5px;
    cursor: pointer;
    font-size: 1.1rem;
    transition: all 0.25s ease;
    min-width: 140px;
    text-align: center;
    text-transform: uppercase;
    font-size: 0.9rem;
  }

  button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  button.primary {
    background: var(--primary);
    color: white;
    margin-left: auto;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    letter-spacing: 1px;
    font-weight: 600;
  }

  button.primary::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px;
    height: 5px;
    background: rgba(255, 255, 255, 0.5);
    opacity: 0;
    border-radius: 100%;
    transform: scale(1, 1) translate(-50%);
    transform-origin: 50% 50%;
  }

  button.primary:focus:not(:active)::after {
    animation: ripple 1s ease-out;
  }

  @keyframes ripple {
    0% {
      transform: scale(0, 0);
      opacity: 0.5;
    }
    100% {
      transform: scale(20, 20);
      opacity: 0;
    }
  }

  button.primary:hover:not(:disabled) {
    background: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  button.primary:active:not(:disabled) {
    transform: translateY(0);
  }

  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    gap: 1.5rem;
    backdrop-filter: blur(5px);
    animation: fadeIn 0.3s ease-out;
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  .loading-message {
    font-size: 1.4rem;
    color: var(--text);
    text-align: center;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
    font-weight: 500;
    padding: 0 2rem;
    animation: fadeIn 0.5s ease-out;
  }

  .loading-subtext {
    color: var(--text-light);
    font-size: 1rem;
    margin-top: -1rem;
    font-style: italic;
  }

  @keyframes spin {
    0% { 
      transform: rotate(0deg) scale(1);
      opacity: 0.8;
    }
    50% {
      transform: rotate(180deg) scale(1.1);
      opacity: 1;
    }
    100% { 
      transform: rotate(360deg) scale(1);
      opacity: 0.8;
    }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .results-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    text-align: left;
    transition: all 0.3s ease;
  }
  
  .results-container.error {
    text-align: center;
    padding: 3rem 2rem;
  }
  
  .error-message h2 {
    color: #dc2626;
    margin-bottom: 1rem;
  }
  
  .error-message p {
    color: #6b7280;
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }

  .evaluation-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
  }
  
  .detail-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
  }
  
  .detail-section.full-width {
    grid-column: 1 / -1;
  }
  
  .detail-section h3 {
    margin-top: 0;
    color: var(--primary);
    border-bottom: 1px solid #e9ecef;
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
  }
  
  .detail-section ul {
    padding-left: 1.25rem;
    margin: 0.5rem 0;
  }
  
  .detail-section li {
    margin-bottom: 0.5rem;
    line-height: 1.5;
  }
  
  .recommendations {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    list-style: none;
    padding: 0;
  }
  
  .recommendations li {
    background: white;
    padding: 1rem;
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .recommendations li:before {
    content: '→';
    color: var(--primary);
    font-weight: bold;
  }
  
  .keyword-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  
  .keyword-tag {
    background: #e9ecef;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    color: #495057;
  }
  
  .motivational-message {
    text-align: center;
    margin: 2rem 0;
    padding: 1.5rem;
    background: #f8f5ff;
    border-radius: 8px;
    border-left: 4px solid #8a63d2;
  }
  
  .motivational-message p {
    margin: 0;
    font-size: 1.1rem;
    color: #5f3dc4;
    font-style: italic;
  }
  
  .score {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary);
    display: block;
    line-height: 1;
  }
  
  .score-label {
    font-size: 0.9rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  
  .scores-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2.5rem 0;
  }

  .valuation {
    text-align: center;
    margin: 2rem 0;
    text-align: left;
    border-radius: 0 var(--radius) var(--radius) 0;
  }

  .valuation-amount {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary);
  }

  .currency-selector {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 1rem;
  }

  .currency-selector select {
    width: auto;
    margin: 0;
  }
</style>
