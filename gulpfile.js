var gulp = require('gulp');
var concat = require('gulp-concat');
var less = require('gulp-less');
var process = require('child_process');


gulp.task('fonts', function(){
  return gulp.src('./node_modules/bootstrap/fonts/*.{ttf,woff,woff2,eot,svg}')
    .pipe(gulp.dest('typeseam/static/fonts/'))
});

gulp.task('img', function(){
  return gulp.src('./frontend/img/*.{png,jpg}')
    .pipe(gulp.dest('typeseam/static/img/'))
});

gulp.task('less_dev', function(){
  return gulp.src('./frontend/less/main.less')
    .pipe(less())
    .pipe(gulp.dest('./typeseam/static/css/'));
});

jsfiles = [
  './node_modules/jquery/dist/jquery.js',
  './frontend/js/main.js',
];

gulp.task('js_dev', function(){
  return gulp.src(jsfiles)
    .pipe(concat('main.js'))
    .pipe(gulp.dest('./typeseam/static/js/'));
})

gulp.task('watch', function(){
  gulp.watch('./frontend/js/**/*.js', ['js_dev']);
  gulp.watch('./frontend/less/**/*.less', ['less_dev']);
})

gulp.task('flask', function(){
  var spawn = process.spawn;
  console.info('Starting flask server');
  var PIPE = {stdio: 'inherit'};
  spawn('python', ['manage.py','server'], PIPE);
});


gulp.task('build', ['fonts', 'img', 'less_dev', 'js_dev'])
gulp.task('default', ['flask', 'build', 'watch'])