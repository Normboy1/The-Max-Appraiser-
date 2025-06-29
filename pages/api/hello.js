// This is a test endpoint to verify API routing is working
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello from the API!' });
}
