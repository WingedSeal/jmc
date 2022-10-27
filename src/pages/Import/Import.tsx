import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const Import = () => {
    return (
        <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-secondary text-3xl md:text-6xl mx-auto">
                Import
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    &emsp;All importing does is practically copying the code
                    from another file to main JMC file. The file name and folder
                    structure does not matter after the import.
                </p>
                <p>
                    &emsp;To import file from{" "}
                    <code>./folder_name/file_name.jmc</code> to{" "}
                    <code>./main.jmc</code>, use the following code in{" "}
                    <code>main.jmc</code>
                </p>
                <CodeBlock>
                    <CodeText type="operator">@import</CodeText>{" "}
                    <CodeText type="string">"folder_name/file_name"</CodeText>;
                </CodeBlock>
                <p>&emsp;This is the folder structure for the import.</p>
                <CodeBlock>
                    ¦&emsp;JMC.exe
                    <br />
                    ¦&emsp;jmc_config.json
                    <br />
                    ¦&emsp;main.jmc
                    <br />
                    ¦ <br />
                    +---folder_name
                    <br />
                    &emsp;&emsp;file_name.jmc
                </CodeBlock>
            </div>
        </section>
    );
};
export default Import;
