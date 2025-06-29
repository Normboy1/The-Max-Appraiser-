// This is a Vercel serverless function for evaluating ideas
export default function handler(req, res) {
  if (req.method === 'POST') {
    // Process POST request
    const { idea, plan, roadmap, currency = 'USD' } = req.body;
    
    // Simple validation
    if (!idea || !plan || !roadmap) {
      return res.status(400).json({ 
        error: 'Missing required fields. Please provide idea, plan, and roadmap.' 
      });
    }

    // Mock evaluation logic (replace with actual implementation)
    const score = Math.floor(Math.random() * 100);
    const valuation = Math.floor(score * 10000);
    
    // Mock response
    const response = {
      grade: score >= 80 ? 'A' : score >= 60 ? 'B' : score >= 40 ? 'C' : 'D',
      score,
      valuation: {
        amount: valuation,
        currency
      },
      evaluation: `Based on our analysis, your idea shows ${score >= 70 ? 'strong' : 'some'} potential.`,
      scores: {
        originality: Math.floor(Math.random() * 100),
        feasibility: Math.floor(Math.random() * 100),
        market_potential: Math.floor(Math.random() * 100),
        technical_merit: Math.floor(Math.random() * 100)
      },
      recommendations: [
        'Consider more detailed market research.',
        'Explore potential technical challenges early.',
        'Validate your idea with potential users.'
      ]
    };

    return res.status(200).json(response);
  } else {
    // Handle any non-POST requests
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ error: `Method ${req.method} not allowed` });
  }
}
