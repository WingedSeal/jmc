import React from "react";
import { Link } from "react-router-dom";

interface ExampleInterfact {
    url: string;
    index: number;
}

const Example: React.FC<ExampleInterfact> = (props) => {
    return (
        <Link
            to={"/try-out?" + props.url}
            className="no-underline text-gray-400 mx-2"
            target="_blank"
            rel="noopener noreferrer"
        >{`Example ${props.index + 1}`}</Link>
    );
};

export default Example;
