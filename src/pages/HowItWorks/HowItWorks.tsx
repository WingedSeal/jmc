import React, { useContext } from "react";

const HowItWorks = () => {
    return (
        <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-primary text-3xl md:text-6xl mx-auto">
                How JMC works
            </div>
            <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Processing JMC file
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;The moment you type <code>compile</code>, the
                    compilation process starts. After reading the configuration,
                    the JMC compiler takes your code from the main JMC file and
                    parses it to tokens, and follows your imports accordingly.
                </p>
                <p className="mt-6">
                    &emsp;Then it reads your header file (<code>main.hjmc</code>
                    ) if there is one, and updates the tokens. Next, it takes
                    care of all JMC-specific features using lexical analysis and
                    creates a virtual datapack. Afterward, it writes that
                    virtual datapack into the actual datapack in the output
                    directory.
                </p>
            </div>
            <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                JMC certificate
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;<code>jmc.txt</code> is a certificate file located at{" "}
                    <code>./data/my_namespace/jmc.txt</code>. Its primary
                    purpose is to prevent you from accidentally overriding your
                    handmade datapack. It's for showing the compiler that this
                    namespace was written by JMC and that the namespace is safe
                    to be deleted. Another use of this file is to save the
                    advanced configuration of JMC. You are allowed to change the
                    content if you understand what you are doing.
                </p>
            </div>
        </section>
    );
};

export default HowItWorks;
