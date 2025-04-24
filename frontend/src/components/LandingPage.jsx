import Head from "next/head";
export default function LandingPage() {
  return (
    <>
      <Head>
        <title>Xpress.ai — AI-powered Tweet Assistant</title>
        <meta
          name="description"
          content="Tailored tweet suggestions, deep analytics, and seamless social engagement with Xpress.ai"
        />
      </Head>

      <main className="flex-grow">
        <section className="hero bg-gray-100 py-20">
          <div className="container mx-auto text-center px-4">
            <h2 className="text-4xl md:text-5xl font-extrabold mb-4">
              Supercharge Your Tweets with AI
            </h2>
            <p className="text-lg md:text-xl text-gray-700 mb-8">
              Craft tweets that resonate. Analyze trends, optimize engagement,
              and keep your unique voice with Xpress.ai.
            </p>
            <a
              href="#get-started"
              className="bg-blue-600 text-white px-8 py-4 rounded-xl text-lg hover:bg-blue-700 transition"
            >
              Try It Free
            </a>
          </div>
        </section>

        <section id="features" className="py-16">
          <div className="container mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 px-4">
            <div className="feature-card p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition">
              <h3 className="text-2xl font-semibold mb-2">
                Personalized Suggestions
              </h3>
              <p className="text-gray-600">
                Leveraging GPT-4o, we learn your style and propose tweets that
                feel like you wrote them.
              </p>
            </div>
            <div className="feature-card p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition">
              <h3 className="text-2xl font-semibold mb-2">Trend Analysis</h3>
              <p className="text-gray-600">
                Stay ahead with real-time mood tracking and trending topic
                alerts from the X API.
              </p>
            </div>
            <div className="feature-card p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition">
              <h3 className="text-2xl font-semibold mb-2">
                Risk & Tone Insights
              </h3>
              <p className="text-gray-600">
                Auto-flag potential risks, suggest supportive, neutral, or
                opposing replies, and maintain brand safety.
              </p>
            </div>
          </div>
        </section>

        <section
          id="how-it-works"
          className="bg-gradient-to-r from-purple-50 to-blue-50 py-16"
        >
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-8">
              How It Works
            </h2>
            <div className="space-y-12">
              <div className="flex flex-col md:flex-row items-center">
                <div className="md:w-1/2">
                  <h3 className="text-2xl font-semibold mb-2">
                    1. Connect Your Account
                  </h3>
                  <p className="text-gray-600">
                    Securely link Xpress.ai to your X account via OAuth to
                    import your tweet history and preferences.
                  </p>
                </div>
                <div className="md:w-1/2 mt-4 md:mt-0">
                  <img
                    src="/images/connect.svg"
                    alt="Connect account illustration"
                    className="mx-auto"
                  />
                </div>
              </div>
              <div className="flex flex-col md:flex-row items-center">
                <div className="md:w-1/2 order-2 md:order-1 mt-4 md:mt-0">
                  <img
                    src="/images/ai-brain.svg"
                    alt="AI analysis illustration"
                    className="mx-auto"
                  />
                </div>
                <div className="md:w-1/2 order-1 md:order-2">
                  <h3 className="text-2xl font-semibold mb-2">
                    2. AI-Powered Analysis
                  </h3>
                  <p className="text-gray-600">
                    Our AI dives into your timeline, identifies high-performing
                    tweets, and captures your unique tone.
                  </p>
                </div>
              </div>
              <div className="flex flex-col md:flex-row items-center">
                <div className="md:w-1/2">
                  <h3 className="text-2xl font-semibold mb-2">
                    3. Get Tailored Suggestions
                  </h3>
                  <p className="text-gray-600">
                    Receive daily tweet prompts, reply ideas, and retweet
                    recommendations to boost engagement.
                  </p>
                </div>
                <div className="md:w-1/2 mt-4 md:mt-0">
                  <img
                    src="/images/suggestions.svg"
                    alt="Suggestions illustration"
                    className="mx-auto"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="contact" className="bg-gray-100 py-16">
          <div className="container mx-auto text-center px-4">
            <h2 className="text-3xl font-bold mb-4">Get in Touch</h2>
            <p className="text-gray-600 mb-6">
              Questions? Feedback? We'd love to hear from you.
            </p>
            <form className="max-w-xl mx-auto grid grid-cols-1 gap-4">
              <input
                type="text"
                placeholder="Your Name"
                className="p-4 rounded-lg border border-gray-300"
              />
              <input
                type="email"
                placeholder="Your Email"
                className="p-4 rounded-lg border border-gray-300"
              />
              <textarea
                placeholder="Your Message"
                className="p-4 rounded-lg border border-gray-300 h-32"
              ></textarea>
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition"
              >
                Send Message
              </button>
            </form>
          </div>
        </section>
      </main>

      <footer className="bg-blue-800 text-white py-8">
        <div className="container mx-auto text-center px-4">
          <p>
            &copy; {new Date().getFullYear()} Xpress.ai. All rights reserved.
          </p>
        </div>
      </footer>
    </>
  );
}
