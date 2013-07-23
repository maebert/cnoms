CNoMS
=====

Content No-Management System. Works like....

![Magic](http://medias.omgif.net/wp-content/uploads/2012/04/Its-magic....gif)


Why?
----

Designers design websites. And nowadays, they also code websites in HTML and CSS. What designers don't want to do is

* Learn complex templating languages
* Set up some obese content-management system
* Configure and maintain a server
* Require clients to learn some obese content-management system
* Make static websites for clients and need to change it twice a week because for said client.
* Use a FTP and configure server addresses to upload their work.

This is where CNoMS (see no mess... get it...?) comes in. The idea is simple:

1. Design and code your pages in standard HTML.
2. Identify editable content by placing simple attributes into your tags, e.g. `<h1 data-fieldname="site title">Dan's Deli</h1>`
3. Drag your project folder (let's say it's called "dansdeli") into the CNoMS app and click "Publish"
4. Your site will be published to [dansdeli.cnoms.com](http://dansdeli.cnoms.com) where everybody can see it
5. Your client can go to [dansdeli.cnoms.com/edit](http://dansdeli.cnoms.com/edit) where he will see the same page - except he can change your editable elements right on the page! Every edtiable element also has a undo-history and you can drag a slider to go through previous versions.

### Other features:

* Reusable elements. Every element with the same name in `data-fieldname` will have the same content across your site.
* Automatic micro-templates. Set up a blog like this:
  
      ```html
      <ul data-fieldname="blog" data-type="collection">
        <li data-type="item">
          <h2 data-fieldname="title">A blog post</h2>
          <div data-fieldname="body">Just lorem ipsum it.</div>
        </li>
      </ul>
      ```

  And CNoMS will analyze the structure, turn everything from `<li>` to `</li>` into a micro-template and let you add more blog posts in the edit view, where they show up just like they will be rendered.
* Local preview - CNoMS also has a "run locally" mode, where you can test your design and make changes.

Current state
-------------

CNoMS already works as advertised, but there is no GUI yet - you'll have to run it from command line. Also, there's no cnoms.com yet - you can only run it locally. If you think that this is a cool project let me know and we can make this reality.

![Mac](https://raw.github.com/maebert/cnoms/master/design/mac/overview.png)


