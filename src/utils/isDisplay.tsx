const isDisplay = (summary: string, searchValue: string, keywords: string) => {
    summary = summary.toLowerCase();
    if (searchValue === "") {
        return true;
    }
    if (summary.includes(searchValue.toLowerCase())) {
        return true;
    }

    let terms = searchValue.match(/(?:[^\s"]+|"[^"]*")+/g); // Split searchValue into multiple terms
    if (terms === null) {
        terms = [searchValue];
    }

    for (let i = 0; i < terms.length; i++) {
        let value = terms[i].toLowerCase();

        if (
            value.length > 1 &&
            value.charAt(0) === '"' &&
            value.charAt(value.length - 1) === '"'
        ) {
            value = value.substring(1, value.length - 1);
        }
        if (summary.includes(value)) {
            return true;
        }
        if (keywords.includes(value)) {
            return true;
        }
    }
    return false;
};

export default isDisplay;
