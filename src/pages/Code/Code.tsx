import React from "react";
import { Link } from "react-router-dom";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";

const Code = () => {
    return (
        <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-primary text-3xl md:text-6xl mx-auto">
                Start coding
            </div>
            <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Main JMC file
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;An empty JMC file will be automatically generated when
                    you finish configuring. The following is the basic template
                    for a simple datapack.
                </p>
                <CodeBlock>
                    say <CodeText type="string">"Load"</CodeText>; <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">__tick__</CodeText>() {"{"}
                    <br />
                    &emsp;say <CodeText type="string">"Loop"</CodeText>;{" "}
                    <CodeText type="comment">
                        // This will run every tick.
                    </CodeText>
                    <br />
                    {"}"}
                </CodeBlock>
                <p className="mt-6">
                    &emsp;To turn JMC file(s) into a Minecraft datapack, simply
                    type compile in the compiler. If you would like it to
                    compile automatically, type{" "}
                    <code>{"autocompile <second>"}</code>. Then you can use{" "}
                    <code>/reload</code> in game. And now, you are ready to go!
                </p>
                <p className="mt-6">
                    JMC will warn you when you get the syntax wrong, so don't
                    worry too much. And don't forget the semicolon! To get more
                    information about the syntax and features, head to{" "}
                    <Link
                        to="/documentation/multiline-command"
                        className="underline"
                    >
                        documentation
                    </Link>{" "}
                    section.
                </p>
            </div>
            <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                JMC Header file
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;Once you learn the basics of JMC. You can start using
                    the header feature. Create <code>main.hjmc</code> file. And
                    then you can start configuring more advanced stuff, like
                    adding comments to the end of every mcfunction file.
                </p>
            </div>
            <CodeBlock>
                <CodeText type="operator">#define</CodeText> loop __tick__
                <br />
                <CodeText type="operator">#credit</CodeText> This datapack is
                made by me.
            </CodeBlock>
        </section>
    );
};

export default Code;
