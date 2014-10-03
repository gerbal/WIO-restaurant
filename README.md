#Rels
Given the quite narrow construction of the site, as I had outlined, there are only links `a href=""` between parent and child resources. I used `rel="parent"` and `rel="child"` to indicate this and describe the relationship between resources.
This description of relationships between resources works well with the simple architecture I have layed out for this assignment, but may not handle a further evolution to a more complicated, itnerelated architecture. 

#form classes
There are two things the forms in this site need to know, one is the name (uuid, effectively) of a resource to be created or deleted, and second the description of a resource to be populated to the hosting page and the new or altered resource.  Third is a reference to the current resource in a way that doesn't require a name or description. `this`
For this the `class=""` of `name`, `description`, and `this` were used for `<input />` elements in our resources.
