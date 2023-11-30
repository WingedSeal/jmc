import React, { ReactElement } from "react";
import { Link } from "react-router-dom";
import isDisplay from "../../utils/isDisplay";
import { scrollToHash } from "../../utils/scrollToHash";

export interface DocsLinkInterface {
    name: string;
    keyword: string;
    page: string;
    searchValue: string;
    sections?: ReactElement<DocsLinkInterface>[];
    hash?: string;
}

const DocsLink: React.FC<DocsLinkInterface> = (props) => {
    const isSelfDisplay = isDisplay(
        props.name,
        props.searchValue,
        props.keyword
    );
    return (
        <>
            {!props.sections ||
            isSelfDisplay ||
            props.sections!.some((DocsLinkSection) => {
                return isDisplay(
                    DocsLinkSection.props.name,
                    props.searchValue,
                    DocsLinkSection.props.keyword
                );
            }) ? (
                <Link
                    to={
                        props.hash
                            ? `/documentation/${props.page}#${props.hash}`
                            : `/documentation/${props.page}`
                    }
                    className="text-white no-underline "
                    onClick={() => {
                        if (
                            props.hash &&
                            window.location.pathname ===
                                `/documentation/${props.page}`
                        )
                            scrollToHash(props.hash);
                    }}
                >
                    <p className="hover:text-gray-300 hover:scale-105">
                        {props.name}
                    </p>
                </Link>
            ) : (
                ""
            )}
            {props.sections?.map(
                (DocsLink, i) =>
                    (isSelfDisplay ||
                        isDisplay(
                            DocsLink.props.name,
                            props.searchValue,
                            DocsLink.props.keyword
                        )) && (
                        <div key={i} className="ml-4">
                            {DocsLink}
                        </div>
                    )
            )}
        </>
    );
};

export default DocsLink;
