import React, { ReactElement } from "react";

interface DocsLinkInterface {
    name: string;
    keyword: string;
    page: string;
    sections?: [ReactElement<DocsLinkInterface>];
    hash?: string;
}

const DocsLink: React.FC<DocsLinkInterface> = (props) => {
    return <div>DocsLink</div>;
};

export default DocsLink;
