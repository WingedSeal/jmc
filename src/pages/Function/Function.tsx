import React from "react";
import { Link } from "react-router-dom";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import useScrollToHash from "../../utils/scrollToHash";

const Function = () => {
    useScrollToHash();
    return (
        <>
            <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-secondary text-3xl md:text-6xl mx-auto">
                    Function
                </div>
                <section id="function_defining" />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Function defining
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Say goodbye to creating a new file for every single
                        function, introducing Function Defining. This feature
                        allows you to define as many functions as you want in a
                        single file. Any capital letter (which is invalid for
                        mcfunction name) will automatically be turned into
                        lowercase, which means it is not case-sensitive. For
                        example, <code>deathMessage</code> is the same as{" "}
                        <code>deathmessage</code>.
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">
                            folder_name.function_name
                        </CodeText>
                        () {"{"} <br />
                        <Tab />
                        say <CodeText type="string">"Code example 1"</CodeText>;
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 2"</CodeText>;
                        <br />
                        {"}"}
                        <br />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">function_name</CodeText>
                        () {"{"} <br />
                        <Tab />
                        say <CodeText type="string">"Code example 3"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                    <p>
                        <Tab />
                        However, there are limitations.{" "}
                        <span className="text-warning">
                            You are not allowed to create parameter(s) like this
                            example.
                        </span>
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">invalidFunction</CodeText>(
                        <CodeText type="error">$parameter</CodeText>) {"{"}{" "}
                        <br />
                        <Tab />
                        say{" "}
                        <CodeText type="string">
                            "This will throw an error."
                        </CodeText>
                        ;<br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Function calling
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Instead of using the <code>/function</code> command, you
                        can use parentheses to call a function. JMC will add a
                        namespace for you automatically. Like function defining,
                        the name is not case-sensitive.
                    </p>
                    <CodeBlock>
                        <CodeText type="function">
                            folder_name.function_name
                        </CodeText>
                        ();{" "}
                        <CodeText type="comment">
                            {"// function namespace:folder_name/function_name"}
                        </CodeText>
                        <br />
                        <CodeText type="function">function_name</CodeText>
                        ();
                        <br />
                        schedule function{" "}
                        <CodeText type="function">function_name</CodeText>
                        ()
                        {" <time> [append|replace];"}
                        <br />
                        schedule clear{" "}
                        <CodeText type="function">function_name</CodeText>
                        ();
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Anonymous Function
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        The archnemesis of every coder is, indeed, naming
                        things. Why bother creating a whole new function just to
                        run a few commands as an entity? You are allowed to run
                        multiple commands in an execute chain in JMC.
                    </p>
                    <CodeBlock>
                        execute <CodeText type="operator">...</CodeText> run{" "}
                        {"{"}
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 1"</CodeText>;
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 2"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                    <p>
                        <Tab />
                        You can also do the same with schedule command. Note
                        that the function will lose its context such as the
                        entity running it like normal schedule command.
                    </p>
                    <CodeBlock>
                        schedule <CodeText type="operator">...</CodeText> {"{"}
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 1"</CodeText>;
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 2"</CodeText>;
                        <br />
                        {"}"} <br />
                        schedule <CodeText type="operator">...</CodeText>{" "}
                        replace {"{"}
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 1"</CodeText>;
                        <br />
                        <Tab />
                        say <CodeText type="string">"Code example 2"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Class (Function grouping)
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        It simply adds extra layers of directory/namespace to
                        any function/
                        <Link to="/documentation/json-files">json</Link>{" "}
                        (Doesn't affect variable) inside it.{" "}
                        <span className="text-warning">
                            {" "}
                            Even though syntax uses the word "class", it is NOT
                            a traditional class.
                        </span>
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">class</CodeText>{" "}
                        <CodeText type="class">folder_one.folder_two</CodeText>{" "}
                        <br />
                        {"{"}
                        <br />
                        <Tab />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">
                            folder_three.function_name
                        </CodeText>
                        () {"{"}
                        <br />
                        <Tab />
                        <Tab />
                        say <CodeText type="string">"Code example 1"</CodeText>;
                        <br />
                        <Tab />
                        <Tab />
                        say <CodeText type="string">"Code example 2"</CodeText>;
                        <br />
                        <Tab />
                        {"}"}
                        <br />
                        <Tab />
                        <CodeText type="keyword">new</CodeText>{" "}
                        <CodeText type="function">file_type</CodeText>
                        (folder_name.json_file_name) {"{"}{" "}
                        <CodeText type="comment">
                            {"//"} See JSON Files page for this feature
                        </CodeText>
                        <br />
                        <Tab />
                        <Tab />
                        JSON_CONTENT
                        <br /> <Tab />
                        {"}"}
                        <br />
                        {"}"}
                        <br />
                        <br />
                        <CodeText type="function">
                            folder_one.folder_two.folder_three.function_name
                        </CodeText>
                        ();
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default Function;
