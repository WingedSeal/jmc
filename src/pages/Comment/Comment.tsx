import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const Comment = () => {
    return (
        <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-primary text-3xl md:text-6xl mx-auto">
                Comments
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-[100%]">
                <p>
                    &emsp;JMC supports both traditional minecraft comment and
                    in-line comment using <code>{"//"}</code>. However,
                    traditional <code>#</code> cannot be used as in-line comment
                    due to conflict with group tag.
                </p>
                <p>Here's an example</p>
                <CodeBlock>
                    <CodeText type="comment">
                        # This function makes the entity says hello world.
                    </CodeText>
                    <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">hello_world</CodeText>() {"{"}
                    <br />
                    &emsp;say <CodeText type="string">
                        "Hello World"
                    </CodeText>;{" "}
                    <CodeText type="comment">// says hello world.</CodeText>
                    <br />
                    {"}"}
                    <br />
                    <CodeText type="comment">// Ends of function</CodeText>
                </CodeBlock>
                <p className="text-warning">&emsp;But you cannot do this.</p>
                <CodeBlock>
                    say <CodeText type="string">"Hello World"</CodeText>;{" "}
                    <CodeText type="error"># says hello world.</CodeText>
                </CodeBlock>
                <p>
                    &emsp;Note that both type of comments will not appear in the
                    final mcfunction file.
                </p>
            </div>
        </section>
    );
};

export default Comment;
