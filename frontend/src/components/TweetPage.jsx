import Head from "next/head";
export default function TweetPage() {
  return (
    <>
      <Head>
        <title>Xpress.ai — AI-powered Tweet Assistant</title>
        <meta
          name="description"
          content="Tailored tweet suggestions, deep analytics, and seamless social engagement with Xpress.ai"
        />
      </Head>

      <h1 className=" heading-xl">
        Enhance Your
        <br />
        Twitter Experience
      </h1>
      <p className="lead mb-6">
        Create engaging content and craft perfect responses
        <br />
        powered by artificial intelligence
      </p>
    </>
  );
}
