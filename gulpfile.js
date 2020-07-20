'use struct'
const gulp = require('gulp');  
const autoprefixer = require('gulp-autoprefixer');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const imagemin = require('gulp-imagemin');
const concat = require('gulp-concat');
const babel = require('gulp-babel');
const browserSync = require('browser-sync').create();
const sass = require('gulp-sass');
sass.compiler = require('node-sass');

function css(){
    return gulp.src('./src/scss/*.scss')
    .pipe(sass.sync().on('error', sass.logError))
    .pipe(autoprefixer({
        browsers: ['last 2 versions'],
        cascade: false
    }))
    .pipe(concat('style.css'))
    /*.pipe(cleanCSS({
        level: 2
      }))*/
    .pipe(gulp.dest("build/css"))
    .pipe(browserSync.stream());
}

function html(){
    return gulp.src('./src/*.html')
    .pipe(gulp.dest('build'))
    .pipe(browserSync.stream());
}

function js(){
    return gulp.src('./src/js/*.js')
    .pipe(concat('scripts.js'))
    .pipe(babel({presets: ['@babel/env']}))
    .pipe(uglify({toplevel:true}))
    .pipe(gulp.dest('build/js'))
    .pipe(browserSync.stream());
}

function image(){
    return gulp.src('./src/image/*')
    .pipe(imagemin())
    .pipe(gulp.dest('build/image'));
}

function watch(){
    browserSync.init({
        server: "./build/"
    });
    gulp.watch("./src/scss/*.scss", gulp.parallel('sass')),
    gulp.watch("./src/js/*.js", gulp.parallel('js')),
    gulp.watch("./src/image/*",gulp.parallel('image')),
    gulp.watch("./src/*.html",gulp.parallel('html'));
}
gulp.task("js",js)
gulp.task("sass", css);
gulp.task("html", html);
gulp.task("image",image);
gulp.task("watch",watch);
gulp.task("start",gulp.series(gulp.parallel("html","sass","js","image"),"watch"));


