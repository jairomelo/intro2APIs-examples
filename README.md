# Medieval Art Collection Analysis

This project aims to analyze the Medieval Art collection of the Metropolitan Museum of Art. The focus of this analysis is on the tags field, which provides a list of terms associated with each object, using controlled vocabularies like the Art and Architecture Thesaurus (AAT) and Wikidata. With that information, we aim to identify thematic areas and explore whether these topics reveal insights about Medieval Art — at least from the perspective of the Metropolitan Museum of Art's metadata, and propose a method to analyze arbitrary terms associated with museum collections.

## Code

Scripts are written in Python and they run on Python 3.10 or later. If you plan to run the code in a lower version of Python, you may get a "TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'". The most straightforward way to fix this is to run the code in a Python 3.10 environment, but if for some reason you need to run it in a lower version, you can use the library `typing` and the `typing.Optional` type hint to fix the error. See this [StackOverflow post](https://stackoverflow.com/questions/76712720/typeerror-unsupported-operand-types-for-type-and-nonetype) for more information.

## License and Right of Use
The data provided by the Metropolitan Museum of Art is published under a [Creative Commons Zero (CC0) license](https://creativecommons.org/publicdomain/zero/1.0/). This means that the data is in the public domain and can be used for any purpose without restriction. The derived data and code written for this project are published under the same license.