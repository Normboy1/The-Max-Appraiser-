<script>
  import { onMount } from 'svelte';
  
  let idea = '';
  let plan = '';
  let roadmap = '';
  let currency = 'USD';
  let currentQuestion = 0;
  let result = null;
  let loading = false;
  let error = null;
  
  const questions = [
    { id: 'idea', label: "What's your idea?" },
    { id: 'plan', label: "What's your plan?" },
    { id: 'roadmap', label: "How do you plan to move forward?" }
  ];
  
  const currencies = [
    { value: 'USD', label: 'USD' },
    { value: 'EUR', label: 'EUR' },
    { value: 'GBP', label: 'GBP' },
    { value: 'JPY', label: 'JPY' }
  ];
  
  function nextQuestion() {
    if (currentQuestion < questions.length - 1) {
      currentQuestion++;
    }
  }
  
  function prevQuestion() {
    if (currentQuestion > 0) {
      currentQuestion--;
    }
  }
  
  function isFormValid() {
    return idea.trim() && plan.trim() && roadmap.trim();
  }
  
  async function handleSubmit(event) {
    event.preventDefault();
    if (!isFormValid()) return;
    
    loading = true;
    error = null;
    
    try {
      const response = await fetch('http://localhost:8000/evaluate/idea', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          idea: idea.trim(),
          plan: plan.trim(),
          roadmap: roadmap.trim(),
          currency: currency
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      result = await response.json();
      
      // Scroll to results
      setTimeout(() => {
        const resultsEl = document.getElementById('result');
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
      
    } catch (err) {
      error = 'Failed to evaluate your idea. Please try again.';
      console.error('Error:', err);
    } finally {
      loading = false;
    }
  }
  
  // Show next question when current one is answered
  $: {
    if (currentQuestion === 0 && idea.trim()) nextQuestion();
    if (currentQuestion === 1 && plan.trim()) nextQuestion();
  }
  
  // Initialize first question as active
  onMount(() => {
    document.querySelector('.question')?.classList.add('active');
  });
</script>

<header>
  <h1>MaxOSL Apraizer</h1>
  <p class="tagline">know your true value</p>
</header>

<main>
  <form on:submit={handleSubmit}>
    {#each questions as question, index}
      <div 
        class="question {index === currentQuestion ? 'active' : ''}"
        style="display: {index <= currentQuestion ? 'block' : 'none'}"
      >
        <label for={question.id}>
          {question.label}
        </label>
        <textarea
          id={question.id}
          bind:value={{ idea, plan, roadmap }[question.id]}
          on:input={() => {}}
          class={{
            answered: { idea, plan, roadmap }[question.id].trim(),
            'fade-in': index === currentQuestion
          }}
          disabled={index > currentQuestion}
          rows="4"
        ></textarea>
      </div>
    {/each}
    
    {#if currentQuestion >= 2}
      <div class="fade-in">
        <label for="currency">Currency</label>
        <select id="currency" bind:value={currency}>
          {#each currencies as curr}
            <option value={curr.value}>
              {curr.label}
            </option>
          {/each}
        </select>
        
        <div class="button-group">
          <button type="button" on:click={prevQuestion} class="secondary">
            Back
          </button>
          <button 
            type="submit" 
            disabled={!isFormValid() || loading}
            class="primary"
          >
            {loading ? 'Evaluating...' : 'Appraise'}
          </button>
        </div>
      </div>
    {/if}
    
    {#if error}
      <div class="error fade-in">
        {error}
      </div>
    {/if}
  </form>
  
  {#if result}
    <section id="result" class="fade-in">
      <h2>Results</h2>
      
      <div id="scores">
        {#each Object.entries({
          'Originality': result.originality,
          'Functional Value': result.functional_value,
          'Scalability': result.scalability,
          'Competition': result.competition
        }) as [label, score]}
          <div class="score-item">
            <div class="score-label">
              <span>{label}</span>
              <span>{(score * 100).toFixed(0)}%</span>
            </div>
            <div class="score-bar">
              <div 
                class="score-fill" 
                style={`width: ${score * 100}%`}
              ></div>
            </div>
          </div>
        {/each}
      </div>
      
      <p id="overall">
        Overall Grade: {result.grade} ({(result.overall_score * 100).toFixed(1)}%)
      </p>
      
      <p id="valuation">
        Estimated Valuation: {result.valuation.amount.toLocaleString()} {result.valuation.currency}
      </p>
      
      {#if result.explanation}
        <p id="explanation">
          {result.explanation}
        </p>
      {/if}
    </section>
  {/if}
</main>

<footer>
  <small>&copy; 2025 MaxOSL</small>
</footer>

<style>
  /* Component styles */
  .button-group {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  button.primary {
    background: var(--primary);
    color: white;
  }
  
  button.secondary {
    background: white;
    color: var(--primary);
    border: 1px solid var(--primary);
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .error {
    color: #dc2626;
    background: #fef2f2;
    padding: 1rem;
    border-radius: 0.375rem;
    margin-top: 1rem;
  }
  
  /* Animation */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .fade-in {
    animation: fadeIn 0.3s ease forwards;
  }
</style>
