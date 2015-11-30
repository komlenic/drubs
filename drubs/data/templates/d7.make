; This makefile is a basic example and includes projects that may be
; unneccessary or inappropriate for some environments or projects. The
; expectation is that developers will carefully evaluate the needs of their
; project and the needs of each environment, uncommenting and including only
; those projects which are appropriate and neccessary.

; Core version
; ------------
; Each makefile should begin by declaring the core version of Drupal that all
; projects should be compatible with.

core = 7.x

; API version
; ------------
; Every makefile needs to declare its Drush Make API version. This version of
; drush make uses API version `2`.

api = 2

; Core project
; ------------
; In order for your makefile to generate a full Drupal site, you must include
; a core project. This is usually Drupal core, but you can also specify
; alternative core projects like Pressflow. Note that makefiles included with
; install profiles *should not* include a core project.

; Drupal 7.x. Requires the `core` property to be set to 7.x.
projects[drupal][version] = "7.41"



; Modules
; --------

; commonly used modules
projects[ctools] = "1.7"
projects[views] = "3.11"
projects[module_filter] = "2.0"
projects[admin_menu] = "3.0-rc5"
projects[libraries] = "2.2"
projects[jquery_update] = "2.5"
projects[wysiwyg] = "2.2"
projects[date] = "2.8"
projects[token] = "1.6"
projects[pathauto] = "1.2"
