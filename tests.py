import unittest
import logging
import jsonpyth as jp


logging.getLogger().setLevel(logging.ERROR)


class TestParse(unittest.TestCase):

    # empty path

    def test_raises_error_for_empty_path(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('')

    # root symbol

    def test_parses_start_root(self):
        result = jp.parse('$')
        self.assert_child_steps((jp.PRoot,), result)

    def test_parses_root_in_path(self):
        result = jp.parse('$.$')
        self.assert_child_steps((jp.PRoot, jp.PRoot), result)
        
    # name property

    def test_parses_name_child(self): 
        result = jp.parse('$.foo') 
        self.assert_child_steps((jp.PRoot, jp.PProperty), result) 
        self.assertEqual('foo', result[1].targets[0].name)

    def test_name_can_include_digit(self): 
        result = jp.parse('$.f00') 
        self.assert_child_steps((jp.PRoot, jp.PProperty), result) 
        self.assertEqual('f00', result[1].targets[0].name)

    def test_raises_error_for_name_leading_digit(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.00f')

    def test_name_can_include_underscore(self):
        result = jp.parse('$.f_o')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('f_o', result[1].targets[0].name)

    def test_raises_error_for_punctuation_in_name(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.f**')

    # double-quoted string property

    def test_parses_double_string_child(self): 
        result = jp.parse('$."foo"') 
        self.assert_child_steps((jp.PRoot, jp.PProperty), result) 
        self.assertEqual('foo', result[1].targets[0].name)

    def test_double_string_can_include_punctuation(self): 
        result = jp.parse('$."f**"') 
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('f**', result[1].targets[0].name)

    def test_double_string_can_include_unicode(self):
        result = jp.parse('$."仮借文字"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('仮借文字', result[1].targets[0].name)
    
    def test_raises_error_for_unclosed_double_string(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$."foo')

    def test_raises_error_for_newline_in_double_string(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$."fo\no"')

    def test_double_string_can_include_escaped_double_quote(self):
        result = jp.parse('$."fo\\"o"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('fo"o', result[1].targets[0].name)

    def test_double_string_can_include_escaped_backslash(self):
        result = jp.parse('$."fo\\\\o"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('fo\\o', result[1].targets[0].name)

    def test_double_string_can_include_single_quote(self):
        result = jp.parse('$."fo\'o"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("fo'o", result[1].targets[0].name)

    def test_double_string_can_start_with_digit(self):
        result = jp.parse('$."00f"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("00f", result[1].targets[0].name)

    def test_double_string_asterisk_is_not_wildcard(self):
        result = jp.parse('$."*"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("*", result[1].targets[0].name)

    def test_double_string_digit_is_not_index(self):
        result = jp.parse('$."9"')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("9", result[1].targets[0].name)

    def test_double_string_preserves_whitespace(self):
        result = jp.parse('$."  f o o  "')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('  f o o  ', result[1].targets[0].name)

    # single-quoted string property

    def test_parses_single_string_child(self): 
        result = jp.parse("$.'foo'") 
        self.assert_child_steps((jp.PRoot, jp.PProperty), result) 
        self.assertEqual('foo', result[1].targets[0].name)

    def test_single_string_can_include_punctuation(self): 
        result = jp.parse("$.'f**'") 
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('f**', result[1].targets[0].name)

    def test_single_string_can_include_unicode(self):
        result = jp.parse("$.'仮借文字'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('仮借文字', result[1].targets[0].name)
    
    def test_raises_error_for_unclosed_single_string(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse("$.'foo")

    def test_raises_error_for_newline_in_single_string(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse("$.'fo\no'")

    def test_single_string_can_include_escaped_single_quote(self):
        result = jp.parse("$.'fo\\'o'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("fo'o", result[1].targets[0].name)

    def test_single_string_can_include_escaped_backslash(self):
        result = jp.parse("$.'fo\\\\o'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("fo\\o", result[1].targets[0].name)

    def test_single_string_can_include_double_quote(self):
        result = jp.parse("$.'fo\"o'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('fo"o', result[1].targets[0].name)

    def test_single_string_can_start_with_digit(self):
        result = jp.parse("$.'00f'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("00f", result[1].targets[0].name)

    def test_single_string_asterisk_is_not_wildcard(self):
        result = jp.parse("$.'*'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("*", result[1].targets[0].name)

    def test_single_string_digit_is_not_index(self):
        result = jp.parse("$.'9'")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual("9", result[1].targets[0].name)

    def test_single_string_preserves_whitespace(self):
        result = jp.parse("$.'  f o o  '")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('  f o o  ', result[1].targets[0].name)

    # child steps

    def test_parses_multiple_child_steps(self):
        result = jp.parse('$.foo.bar.weh.blah')
        self.assert_types((jp.PChild, jp.PChild, jp.PChild, jp.PChild, jp.PChild), result)

    def test_parses_first_child_step_without_root(self):
        result = jp.parse('.foo')
        self.assert_types((jp.PChild,), result)
        self.assert_types((jp.PProperty,), result[0].targets)
        self.assertEqual('foo', result[0].targets[0].name)

    def test_parses_implicit_first_child_step_without_dot(self):
        result = jp.parse('foo')
        self.assert_types((jp.PChild,), result)
        self.assert_types((jp.PProperty,), result[0].targets)
        self.assertEqual('foo', result[0].targets[0].name)

    def test_raises_error_for_child_dot_without_target(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.')

    def test_parses_square_bracketted_child_step(self):
        result = jp.parse('$[foo]')
        self.assert_types((jp.PChild, jp.PChild), result)
        self.assert_types((jp.PProperty,), result[1].targets)
        self.assertEqual('foo', result[1].targets[0].name)

    def test_parses_multiple_square_bracket_steps(self):
        result = jp.parse('$[foo][bar]')
        self.assert_types((jp.PChild, jp.PChild, jp.PChild), result)
        self.assert_types((jp.PProperty,), result[1].targets)
        self.assertEqual('foo', result[1].targets[0].name)
        self.assert_types((jp.PProperty,), result[2].targets)
        self.assertEqual('bar', result[2].targets[0].name)

    def test_parses_mixed_dotted_and_bracketted_child_steps(self):
        result = jp.parse('$.foo[bar].weh')
        self.assert_child_steps((jp.PRoot, jp.PProperty, jp.PProperty, jp.PProperty), result)

    def test_raises_error_for_unclosed_square_bracket(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$[foo')

    def test_raises_error_for_child_with_both_dot_and_square_brackets(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.[foo]')

    def test_raises_error_for_step_with_both_double_dot_and_square_brackets(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$..[foo]')

    def test_raises_error_for_square_bracket_without_target(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$[]')

    def test_parses_square_bracketted_root(self):
        result = jp.parse('[$]')
        self.assert_child_steps((jp.PRoot,),result)

    def test_parses_square_bracketted_double_string(self):
        result = jp.parse('$["foo"]')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)   
        self.assertEqual('foo', result[1].targets[0].name)

    def test_parses_square_bracketted_single_string(self):
        result = jp.parse("$['foo']")
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)
        self.assertEqual('foo', result[1].targets[0].name)

    # recursive step

    def test_parses_name_recursive(self):
        result = jp.parse('$..foo')
        self.assert_types((jp.PChild, jp.PRecursive), result)
        self.assert_types((jp.PProperty,), result[1].targets)
        self.assertEqual('foo', result[1].targets[0].name)

    def test_parses_mixed_child_and_recursive_steps(self):
        result = jp.parse('$.foo..bar.weh..blah')
        self.assert_types((jp.PChild, jp.PChild, jp.PRecursive, jp.PChild, jp.PRecursive), result)

    def test_parses_first_recursive_step_without_root(self):
        result = jp.parse('..foo')
        self.assert_types((jp.PRecursive,), result)
        self.assert_types((jp.PProperty,), result[0].targets)
        self.assertEqual('foo', result[0].targets[0].name)

    # whitespace

    def test_ignores_spaces(self):
        result = jp.parse('      $  .    foo       ')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)

    def test_ignores_newlines(self):
        result = jp.parse('\n\n$\n.\n\nfoo\n\n\n')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)

    def test_ignores_tabs(self):
        result = jp.parse('\t\t$\t.\t\tfoo\t\t\t')
        self.assert_child_steps((jp.PRoot, jp.PProperty), result)

    # current node symbol

    def test_parses_current_node_symbol(self):
        result = jp.parse('$.@')
        self.assert_child_steps((jp.PRoot, jp.PCurrent), result)

    def test_parses_current_node_at_start(self):
        result = jp.parse('@.foo')
        self.assert_child_steps((jp.PCurrent, jp.PProperty), result)

    def test_parses_square_bracketted_current_node_symbol(self):
        result = jp.parse('$[@]')
        self.assert_child_steps((jp.PRoot, jp.PCurrent), result)

    # wildcard symbol

    def test_parses_wildcard(self):
        result = jp.parse('$.*')
        self.assert_child_steps((jp.PRoot, jp.PWildcard), result)

    def test_parses_wildcard_at_start(self):
        result = jp.parse('*.foo')
        self.assert_child_steps((jp.PWildcard, jp.PProperty), result)

    def test_parses_square_bracketted_wildcard(self):
        result = jp.parse('$[*]')
        self.assert_child_steps((jp.PRoot, jp.PWildcard), result)

    # multiple targets

    def test_parses_two_targets_for_step(self):
        result = jp.parse('$.foo,bar')
        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty)), result)
        self.assertEqual('foo', result[1].targets[0].name)
        self.assertEqual('bar', result[1].targets[1].name)

    def test_parses_more_than_two_targets_for_step(self):
        result = jp.parse('$.foo,bar,weh,blah')
        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty, jp.PProperty, jp.PProperty)), result)
        self.assertEqual('foo', result[1].targets[0].name)
        self.assertEqual('bar', result[1].targets[1].name)
        self.assertEqual('weh', result[1].targets[2].name)
        self.assertEqual('blah',result[1].targets[3].name)

    def test_parses_mixed_target_types(self):
        result = jp.parse('$.foo,"bar",*,@')
        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty, jp.PWildcard, jp.PCurrent)), result)
        self.assertEqual('foo', result[1].targets[0].name)
        self.assertEqual('bar', result[1].targets[1].name)

    def test_raises_error_for_trailing_comma_on_targets(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.foo,')

    def test_parses_multiple_multitarget_steps(self):
        result = jp.parse('$.foo,bar.weh,blah')
        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty), (jp.PProperty, jp.PProperty)), result)    

    def test_parses_square_bracketted_multiple_targets(self):
        result = jp.parse('$[foo,bar]')
        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty)), result)
        self.assertEqual('foo', result[1].targets[0].name)
        self.assertEqual('bar', result[1].targets[1].name)

    def test_raises_error_for_empty_target_in_target_set(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.foo,,bar')

    def test_raises_error_for_child_brackets_inside_target_set(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.foo,[bar]')

#    def test_parses_multiple_targets_with_single_quoted_comma(self):
#        result = jp.parse("$.foo','bar")
#        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty)), result)
#        self.assertEqual('foo', result[1].targets[0].name)
#        self.assertEqual('bar', result[1].targets[1].name)
#
#    def test_parses_multiple_single_quoted_properties_with_single_quoted_comma(self):
#        result = jp.parse("$.'foo'',''bar'")
#        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty)), result)
#        self.assertEqual('foo', result[1].targets[0].name)
#        self.assertEqual('bar', result[1].targets[1].name)
#
#    def test_parses_multiple_targets_with_double_quoted_comma(self):
#        result = jp.parse('$.foo","bar')
#        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty)), result)
#        self.assertEqual('foo', result[1].targets[0].name)
#        self.assertEqual('bar', result[1].targets[1].name)
#
#    def test_parses_multiple_double_quoted_properties_with_double_quoted_comma(self):
#        result = jp.parse('$."foo"",""bar"')
#        self.assert_child_steps((jp.PRoot, (jp.PProperty, jp.PProperty)), result)
#        self.assertEqual('foo', result[1].targets[0].name)
#        self.assertEqual('bar', result[1].targets[1].name)
        
    # slices

    def test_parses_simple_index(self):
        result = jp.parse('$.1')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertTrue(hasattr(targ, 'index'))
        self.assertFalse(hasattr(targ, 'start'))
        self.assertFalse(hasattr(targ, 'end'))
        self.assertFalse(hasattr(targ, 'step'))
        self.assertEqual(1, targ.index)

    def test_parses_negative_index(self):
        result = jp.parse('$.-1')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertTrue(hasattr(targ, 'index'))
        self.assertEqual(-1, targ.index)

    def test_parses_canonical_slice(self):
        result = jp.parse('$.1:2:3')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertFalse(hasattr(targ, 'index'))
        self.assertTrue(hasattr(targ, 'start'))
        self.assertTrue(hasattr(targ, 'end'))
        self.assertTrue(hasattr(targ, 'step'))
        self.assertEqual(1, targ.start)
        self.assertEqual(2, targ.end)
        self.assertEqual(3, targ.step)

    def test_parses_negatives_in_canonical_slice(self):
        result = jp.parse('$.-1:-2:-3')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertEqual(-1, targ.start)
        self.assertEqual(-2, targ.end)
        self.assertEqual(-3, targ.step)

    def test_parses_toend_slice(self):
        result = jp.parse('$.1:')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertFalse(hasattr(targ, 'index'))
        self.assertTrue(hasattr(targ, 'start'))
        self.assertFalse(hasattr(targ, 'end'))
        self.assertFalse(hasattr(targ, 'step'))
        self.assertEqual(1, targ.start)

    def test_parses_fromstart_slice(self):
        result = jp.parse('$.:1')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertFalse(hasattr(targ, 'index'))
        self.assertFalse(hasattr(targ, 'start'))
        self.assertTrue(hasattr(targ, 'end'))
        self.assertFalse(hasattr(targ, 'step'))
        self.assertEqual(1, targ.end)

    def test_parses_allwithstep_slice(self):
        result = jp.parse('$.::1')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertFalse(hasattr(targ, 'index'))
        self.assertFalse(hasattr(targ, 'start'))
        self.assertFalse(hasattr(targ, 'end'))
        self.assertTrue(hasattr(targ, 'step'))
        self.assertEqual(1, targ.step)

    def test_parses_all_slice(self):
        result = jp.parse('$.:')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertFalse(hasattr(targ, 'index'))
        self.assertFalse(hasattr(targ, 'start'))
        self.assertFalse(hasattr(targ, 'end'))
        self.assertFalse(hasattr(targ, 'step'))

    def test_parses_other_slice_combinations(self):
        for sl,ix,st,en,sp in [
                    # :
                    # :1
                    # 1:
                    ('1:2', False,1,    2,    False),
                    ('::',  False,False,False,False),
                    # ::1
                    (':1:', False,False,1,    False),
                    (':1:2',False,False,1,    2    ),
                    ('1::', False,1,    False,False),
                    ('1::2',False,1,    False,2    ),
                    ('1:2:',False,1,    2,    False)
                    # 1:2:3
                ]:
            with self.subTest(slice=sl):
                result = jp.parse('$.{}'.format(sl))
                self.assert_child_steps((jp.PRoot, jp.PSlice), result)
                targ = result[1].targets[0]
                for p,v in [('index',ix),('start',st),('end',en),('step',sp)]:
                    if v is False: 
                        self.assertFalse(hasattr(targ, p))
                    else:
                        self.assertEqual(v, getattr(targ, p))

    def test_parses_square_bracketted_slice(self):
        result = jp.parse('$[1:2]')
        self.assert_child_steps((jp.PRoot, jp.PSlice), result)
        targ = result[1].targets[0]
        self.assertFalse(hasattr(targ, 'index'))
        self.assertTrue(hasattr(targ, 'start'))
        self.assertTrue(hasattr(targ, 'end'))
        self.assertFalse(hasattr(targ, 'step'))
        self.assertEqual(1, targ.start)
        self.assertEqual(2, targ.end)

    # expressions

    def test_parses_expression_child_step(self):
        result = jp.parse('$.(1+1)')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('1+1', result[1].targets[0].code)

    def test_expression_can_contain_other_path_symbols(self):
        result = jp.parse('$.($@0f!仮*:[].?,)')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('$@0f!仮*:[].?,', result[1].targets[0].code)

    def test_expression_can_contain_escaped_round_brackets(self):
        result = jp.parse('$.(\\(1+1\\)*5)')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('(1+1)*5', result[1].targets[0].code)

    def test_expression_can_contain_escaped_backslash(self):
        result = jp.parse('$.(\\\\)')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('\\', result[1].targets[0].code)

    def test_expression_can_contain_escaped_newline(self):
        result = jp.parse('$.(\\n)')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('\n', result[1].targets[0].code)

    def test_expression_preserves_whitespace(self):
        result = jp.parse('$.(  1 + 1  )')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('  1 + 1  ', result[1].targets[0].code)

    def test_raises_error_for_expression_without_closing_bracket(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.(1+1')

    def test_raises_error_for_expression_containing_newline(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.(1\n+\n1)')

    def test_parses_square_bracketted_expression(self):
        result = jp.parse('$[(1+1)]')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('1+1', result[1].targets[0].code)

    def test_parses_empty_expression(self):
        result = jp.parse('$.()')
        self.assert_child_steps((jp.PRoot, jp.PExpression), result)
        self.assertEqual('', result[1].targets[0].code)

    # filters

    def test_parses_filter_child_step(self):
        result = jp.parse('$.?(1+1)')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('1+1', result[1].targets[0].code)

    def test_filter_can_contain_other_path_symbols(self):
        result = jp.parse('$.?($@0f!仮*:[].?,)')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('$@0f!仮*:[].?,', result[1].targets[0].code)

    def test_filter_can_contain_escaped_round_brackets(self):
        result = jp.parse('$.?(\\(1+1\\)*5)')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('(1+1)*5', result[1].targets[0].code)

    def test_filter_can_contain_escaped_backslash(self):
        result = jp.parse('$.?(\\\\)')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('\\', result[1].targets[0].code)

    def test_filter_can_contain_escaped_newline(self):
        result = jp.parse('$.?(\\n)')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('\n', result[1].targets[0].code)

    def test_filter_preserves_whitespace(self):
        result = jp.parse('$.?(  True  or  False  )')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('  True  or  False  ', result[1].targets[0].code)

    def test_raises_error_for_filter_without_closing_bracket(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.?(1+1')

    def test_raises_error_for_filter_containing_newline(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.?(1\n+\n1)')

    def test_parses_square_bracketted_filter(self):
        result = jp.parse('$[?(1+1)]')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('1+1', result[1].targets[0].code)

    def test_parses_empty_filter(self):
        result = jp.parse('$.?()')
        self.assert_child_steps((jp.PRoot, jp.PFilter), result)
        self.assertEqual('', result[1].targets[0].code)

    # general bad input

    def test_raises_error_for_invalid_child_target(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$.~')

    def test_raises_error_for_invalid_square_bracketted_child_target(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('$[~]')

    def test_raises_error_for_invalid_child_target_at_start(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('.~')

    def test_raises_error_for_invalid_implicit_child_target(self):
        with self.assertRaises(jp.JsonPathSyntaxError):
            jp.parse('~')

    # helper methods

    def assert_types(self, expected, result):
        self.assertEqual(expected, tuple(type(s) for s in result))

    def assert_child_steps(self, expected, result):
        targs = []
        for s in result:
            self.assertEqual(jp.PChild, type(s))
            targs.append(tuple(type(t) for t in s.targets) if len(s.targets) > 1 else type(s.targets[0]))
        self.assertEqual(expected, tuple(targs))


class TestEvaluate(unittest.TestCase):

    example = {
        "store": {
            "book": [
                {
                    "category": "reference",
                    "author": "Nigel Rees",
                    "title": "Sayings of the Century",
                    "price": 8.95,
                },
                {
                    "category": "fiction",
                    "author": "Evelyn Waugh",
                    "title": "Sword of Honour",
                    "price": 12.99,
                },
                {
                    "category": "fiction",
                    "author": "Herman Melville",
                    "title": "Moby Dick",
                    "isbn": "0-553-21311-3",
                    "price": 8.99,
                },
                {
                    "category": "fiction",
                    "author": "J. R. R. Tolkien",
                    "title": "The Lord of the Rings",
                    "isbn": "0-395-19395-8",
                    "price": 22.99,
                },
            ],
            "bicycle": {
                "color": "red",
                "price": 19.95,
            },
        }
    }

    # root & property child steps

    def test_evaluates_root_child(self):
        result = jp.evaluate({"a":1,"b":[2,3]}, [jp.PChild(targets=[jp.PRoot()])])
        self.assertEqual([( {"a":1,"b":[2,3]}, '$' )], result)

    def test_evaluates_property_child(self):
        result = jp.evaluate({"a":1,"b":[2,3]}, [jp.PChild(targets=[jp.PProperty(name='b')])])
        self.assertEqual([( [2,3], '$["b"]' )], result)

    def test_evaluates_root_mid_path(self):
        result = jp.evaluate({"a":1,"b":[2,3]}, 
                             [jp.PChild(targets=[jp.PRoot()]), jp.PChild(targets=[jp.PProperty(name='b')]), 
                              jp.PChild(targets=[jp.PRoot()]), jp.PChild(targets=[jp.PProperty(name='a')])] )
        self.assertEqual([( 1, '$["a"]' )], result)

    def test_evaluates_nested_child_properties(self):
        result = jp.evaluate({"a":{"b":1,"c":2},"d":3},
                             [jp.PChild(targets=[jp.PProperty(name='a')]), jp.PChild(targets=[jp.PProperty(name='b')])])
        self.assertEqual([( 1, '$["a"]["b"]' )], result)

    # current node

    def test_evaluates_current_child(self):
        result = jp.evaluate({"a":{"b":1,"c":2},"d":3},
                             [jp.PChild(targets=[jp.PProperty(name='a')]), jp.PChild(targets=[jp.PCurrent()]),
                              jp.PChild(targets=[jp.PProperty(name='c')])] )
        self.assertEqual([( 2, '$["a"]["c"]' )], result)

    # target sets

    def test_evaluates_multipletarget_child(self):
        result = jp.evaluate({"a":{"b":1,"c":2},"d":3},
                             [jp.PChild(targets=[jp.PProperty(name='a')]),
                              jp.PChild(targets=[jp.PProperty(name='b'),jp.PProperty(name='c')])] )
        self.assertEqual([( 1, '$["a"]["b"]' ), ( 2, '$["a"]["c"]' )], result)

    def test_evaluates_multipletarget_child_mid_path(self):
        result = jp.evaluate({"a":{"b":{"c":1,"d":2},"e":{"c":3,"d":4}},"f":0},
                             [jp.PChild(targets=[jp.PProperty(name='a')]),
                              jp.PChild(targets=[jp.PProperty(name='b'),jp.PProperty(name='e')]),
                              jp.PChild(targets=[jp.PProperty(name='c')])] )
        self.assertEqual([( 1, '$["a"]["b"]["c"]' ), ( 3, '$["a"]["e"]["c"]' )], result)

    def test_evaluates_nested_multipletarget_child_steps(self):
        result = jp.evaluate({"A":{"i":1,"ii":2,"iii":3},
                              "B":{"i":4,"ii":5,"iii":6},
                              "C":{"i":7,"ii":8,"iii":9}},
                             [jp.PChild(targets=[jp.PProperty(name='A'),jp.PProperty(name='C')]),
                              jp.PChild(targets=[jp.PProperty(name='ii'),jp.PProperty(name='iii')])] )
        self.assertEqual([( 2, '$["A"]["ii"]' ), ( 8, '$["C"]["ii"]' ),
                          ( 3, '$["A"]["iii"]' ), ( 9, '$["C"]["iii"]' )], result)

    # wildcards                 
                          
    def test_evaluates_wildcard_child_for_dict(self):
        result = jp.evaluate({"a":1,"b":2,"c":[3,4]},
                             [jp.PChild(targets=[jp.PWildcard()])] )
        self.assertEqual([( 1, '$["a"]' ), ( 2, '$["b"]' ), ( [3,4], '$["c"]' )], result)

    def test_evaluates_wildcard_child_for_sequence(self):
        result = jp.evaluate([1, 2, [3,4]],
                             [jp.PChild(targets=[jp.PWildcard()])] )
        self.assertEqual([(1, '$[0]'), (2, '$[1]'), ([3,4], '$[2]')], result)

    def test_evaluates_wildcard_mid_path(self):
        result = jp.evaluate({"a":1,"b":[{"i":1,"ii":2},{"i":3,"ii":4},{"i":5,"ii":6}]},
                             [jp.PChild(targets=[jp.PProperty(name='b')]),
                              jp.PChild(targets=[jp.PWildcard()]),
                              jp.PChild(targets=[jp.PProperty(name='ii')])] )
        self.assertEqual([(2, '$["b"][0]["ii"]'), (4, '$["b"][1]["ii"]'), 
                          (6, '$["b"][2]["ii"]')], result)

    def test_evaluates_nested_wildcard_steps(self):
        result = jp.evaluate({ "i":{"a":[{"a":1,"b":2},{"a":3,"b":4}],
                                    "b":[{"a":5,"b":6},{"a":7,"b":8}]},
                              "ii":{"a":[{"a":9,"b":1},{"a":2,"b":3}],
                                    "b":[{"a":4,"b":5},{"a":6,"b":7}]} },
                             [jp.PChild(targets=[jp.PWildcard()]), jp.PChild(targets=[jp.PProperty(name='a')]),
                              jp.PChild(targets=[jp.PWildcard()]), jp.PChild(targets=[jp.PProperty(name='b')])] )
        self.assertEqual([(2, '$["i"]["a"][0]["b"]'), (4, '$["i"]["a"][1]["b"]'), 
                          (1, '$["ii"]["a"][0]["b"]'),(3, '$["ii"]["a"][1]["b"]')], result)

    def test_evaluates_multiple_wildcard_targets_by_duplicating(self):
        result = jp.evaluate([4,2],
                             [jp.PChild(targets=[jp.PWildcard(),jp.PWildcard()])] )
        self.assertEqual([(4, '$[0]'), (2, '$[1]'), (4, '$[0]'), (2, '$[1]')], result)

    # slices
    
    def test_evaluates_simple_index_slice(self):
        result = jp.evaluate(["a","b","c","d","e"],
                             [jp.PChild(targets=[jp.PSlice(index=3)])])
        self.assertEqual([("d", '$[3]')], result)

    def test_evaluates_slice_with_step(self):
        result = jp.evaluate(["a","b","c","d","e","f","g"],
                             [jp.PChild(targets=[jp.PSlice(start=1,end=5,step=2)])] )
        self.assertEqual([('b', '$[1]'), ('d', '$[3]')], result)
                    
    def test_evaluates_slice_without_step(self):
        result = jp.evaluate(["a","b","c","d","e"],
                             [jp.PChild(targets=[jp.PSlice(start=1,end=3)])] )
        self.assertEqual([('b', '$[1]'), ('c', '$[2]')], result)
        
    def test_evaluates_slice_without_end(self):
        result = jp.evaluate(["a","b","c","d"],
                             [jp.PChild(targets=[jp.PSlice(start=2)])] )
        self.assertEqual([('c', '$[2]'), ('d', '$[3]')], result)

    def test_evaluates_slice_without_start(self):
        result = jp.evaluate(["a","b","c","d"],
                             [jp.PChild(targets=[jp.PSlice(end=2)])] )
        self.assertEqual([('a', '$[0]'), ('b', '$[1]')], result)

    def test_evaluates_slice_with_negative_start(self):
        result = jp.evaluate(["a","b","c","d"],
                             [jp.PChild(targets=[jp.PSlice(start=-2)])] )
        self.assertEqual([('c', '$[2]'), ('d', '$[3]')], result)

    def test_evaluates_slice_with_negative_end(self):
        result = jp.evaluate(["a","b","c","d"],
                             [jp.PChild(targets=[jp.PSlice(end=-1)])] )
        self.assertEqual([('a', '$[0]'), ('b', '$[1]'), ('c', '$[2]')], result)

    def test_evaluates_slice_with_negative_step(self):
        result = jp.evaluate(["a","b","c","d"],
                             [jp.PChild(targets=[jp.PSlice(step=-2)])] )
        self.assertEqual([('d', '$[3]'), ('b', '$[1]')], result)        

    def test_evaluates_slice_mid_path(self):
        result = jp.evaluate({"a":[{"i":1,"ii":2},{"i":3,"ii":4},
                                   {"i":5,"ii":6},{"i":7,"ii":8}]},
                             [jp.PChild(targets=[jp.PProperty(name='a')]),
                              jp.PChild(targets=[jp.PSlice(start=1,end=3)]),
                              jp.PChild(targets=[jp.PProperty(name='ii')])] )
        self.assertEqual([(4, '$["a"][1]["ii"]'), (6, '$["a"][2]["ii"]')], result)

    def test_evaluates_nested_slice_steps(self):
        result = jp.evaluate([{"a":["x","y"],"b":["z","x"]},{"a":["y","z"],"b":["x","y"]},
                              {"a":["z","x"],"b":["y","z"]},{"a":["x","y"],"b":["z","x"]}],
                             [jp.PChild(targets=[jp.PSlice(start=1,end=3)]),
                              jp.PChild(targets=[jp.PProperty(name='a')]),
                              jp.PChild(targets=[jp.PSlice(index=1)])] )
        self.assertEqual([('z', '$[1]["a"][1]'), ('x', '$[2]["a"][1]')], result)

    def test_evaluates_multiple_slice_targets(self):
        result = jp.evaluate(['a','b','c'],
                             [jp.PChild(targets=[jp.PSlice(start=1),jp.PSlice(end=-1)])] )
        self.assertEqual([('b', '$[1]'), ('c', '$[2]'), ('a', '$[0]'), ('b', '$[1]')], result)

    # recursive steps

    def test_evaluates_recursive_step(self):
        result = jp.evaluate({"c":{"a":{"a":1},"b":2},"b":[{"a":2},4],"a":0},
                             [jp.PRecursive(targets=[jp.PProperty(name='a')])] )
        self.assertEqual([(0, '$["a"]'), ({"a":1}, '$["c"]["a"]'), (1, '$["c"]["a"]["a"]'), 
                          (2, '$["b"][0]["a"]')], result)

    def test_evaluates_recursive_step_with_multiple_targets(self):
        result = jp.evaluate({"c":{"a":{"a":1},"b":2},"b":[{"a":2},4],"a":0},
                             [jp.PRecursive(targets=[jp.PProperty(name='a'),jp.PProperty(name='b')])] )
        self.assertEqual([(0, '$["a"]'), ([{"a":2},4], '$["b"]'), ({"a":1}, '$["c"]["a"]'), 
                          (2, '$["c"]["b"]'), (1, '$["c"]["a"]["a"]'),
                          (2, '$["b"][0]["a"]')], result)

    def test_evaluates_nested_recursive_steps(self):
        result = jp.evaluate({"a":{"a":{"b":1},"b":3},"b":{"a":{"a":5,"b":{"b":2}},"b":4}},
                             [jp.PRecursive(targets=[jp.PProperty(name='a')]),
                              jp.PRecursive(targets=[jp.PProperty(name='b')])])
        self.assertEqual([(3, '$["a"]["b"]'), (1, '$["a"]["a"]["b"]'), 
                          ({"b":2}, '$["b"]["a"]["b"]'), (1, '$["a"]["a"]["b"]'),
                          (2, '$["b"]["a"]["b"]["b"]')], result)

    # expressions

    def test_evaluates_expression_child_for_key(self):
        result = jp.evaluate({"bar":1, "foo":2, "weh":3},
                             [jp.PChild(targets=[jp.PExpression(code='"foo"')])] )
        self.assertEqual([(2, '$["foo"]')], result)

    def test_evaluates_expression_child_for_index(self):
        result = jp.evaluate([1,2,3],
                             [jp.PChild(targets=[jp.PExpression(code='1')])] )
        self.assertEqual([(2, '$[1]')], result)
    
    def test_evaluates_non_string_expression_for_key(self):
        result = jp.evaluate({"True":1, "False":2, "None":3},
                             [jp.PChild(targets=[jp.PExpression(code='True')])] )
        self.assertEqual([(1, '$["True"]')], result)

    def test_evaluates_non_int_expression_for_index(self):
        result = jp.evaluate([1,2,3],
                             [jp.PChild(targets=[jp.PExpression(code='False')])] )
        self.assertEqual([(1, '$[0]')], result)

    def test_evaluates_operators_in_expression(self):
        result = jp.evaluate([1,2,3,4,5],
                             [jp.PChild(targets=[jp.PExpression(code='2**3/(2+2)')])] )
        self.assertEqual([(3, '$[2]')], result)

    def test_evaluates_current_node_in_expression(self):
        result = jp.evaluate([1,2,3,4,5],
                             [jp.PChild(targets=[jp.PExpression(code='@[2]+1')])] )
        self.assertEqual([(5, '$[4]')], result)

    def test_raises_error_for_bad_syntax_in_expression(self):
        with self.assertRaises(jp.PythonSyntaxError):
            jp.evaluate([1,2,3,4,5],
                        [jp.PChild(targets=[jp.PExpression(code='^!*&~')])] )
        
    def test_evaluates_expression_with_builtins(self):
        result = jp.evaluate([1,2,3,4,5],
                             [jp.PChild(targets=[jp.PExpression(code='len("foo")')])] )
        self.assertEqual([(4, '$[3]')], result)

    def test_evaluates_escaped_at_symbol_in_expression_as_plain_at(self):
        result = jp.evaluate({"@":1,"~":2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\@"')])] )
        self.assertEqual([(1, '$["@"]')], result)

    def test_evaluates_expression_with_actual_backslash_preceeding_current_node(self):
        result = jp.evaluate({"\\__current":1,"~":2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\\\@"')])] )
        self.assertEqual([(1, '$["\\\\__current"]')], result)

    def test_evaluates_escaped_at_symbol_with_multiple_actual_backslashes_preceeding(self):
        result = jp.evaluate({'\\\\@':1,'~':2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\\\\\\\\\@"')])] )
        self.assertEqual([(1, '$["\\\\\\\\@"]')], result)

    def test_evaluates_current_node_with_multiple_actual_backslashes_preceeding(self):
        result = jp.evaluate({"\\\\__current":1,"~":2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\\\\\\\@"')])] )
        self.assertEqual([(1, '$["\\\\\\\\__current"]')], result)

    def test_evaluates_root_node_in_expression(self):
        result = jp.evaluate({'a':['i','ii','iii'],'b':1},
                             [jp.PChild(targets=[jp.PProperty(name='a')]),
                              jp.PChild(targets=[jp.PExpression(code='$["b"]')])] )
        self.assertEqual([('ii', '$["a"][1]')], result)

    def test_evaluates_escaped_dollar_symbol_in_expression_as_plain_dollar(self):
        result = jp.evaluate({"~":1,"$":2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\$"')])] )
        self.assertEqual([(2, '$["$"]')], result)

    def test_evaluates_expression_with_actual_backslash_preceeding_root_node(self):
        result = jp.evaluate({'\\__root':1,'~':2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\\\$"')])] )
        self.assertEqual([(1, '$["\\\\__root"]')], result)

    def test_evaluates_escaped_dollar_symbol__with_multiple_actual_backslashes_preceeding(self):
        result = jp.evaluate({'\\\\$':1,'~':2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\\\\\\\\\$"')])] )
        self.assertEqual([(1, '$["\\\\\\\\$"]')], result)

    def test_evaluates_root_node_with_multiple_actual_backslashes_preceeding(self):
        result = jp.evaluate({'\\\\__root':1,'~':2},
                             [jp.PChild(targets=[jp.PExpression(code='"\\\\\\\\$"')])] )
        self.assertEqual([(1, '$["\\\\\\\\__root"]')], result)

#    def test_doesnt_replace_at_symbol_in_single_string(self):
#        result = jp.evaluate({"@":1,"~":2},
#                             [jp.PChild(targets=[jp.PExpression(code="'@'")])] )
#        self.assertEqual([(1, '$["@"]')], result)
#
#    def test_doesnt_replace_at_symbol_in_double_string(self):
#        result = jp.evaluate({"@":1,"~":2},
#                             [jp.PChild(targets=[jp.PExpression(code='"@"')])] )
#        self.assertEqual([(1, '$["@"]')], result)
#
#    def test_doesnt_replace_at_symbol_in_triple_string(self):
#        result = jp.evaluate({"@":1, "~":2},
#                             [jp.PChild(targets=[jp.PExpression(code='"""@"""')])] )
#        self.assertEqual([(1, '$["@"]')], result)
#
#    def test_doesnt_replace_at_symbol_in_multiline_triple_string(self): 
#        result = jp.evaluate({'\n@\n':1, '~':2},
#                             [jp.PChild(targets=[jp.PExpression(code='"""\\n@\\n"""')])] )
#        self.assertEqual([(1, '$["\\n@\\n"]')], result)
#
#    def test_doesnt_replace_at_symbol_in_double_string_with_escaped_quote(self):
#        result = jp.evaluate({'"+str(len(@))+"':1, "~":2},
#                             [jp.PChild(targets=[jp.PExpression(code='"\\"+str(len(@))+\\""')])] )
#        self.assertEqual([(1, '$["\\"+str(len(@))+\\""]')], result)
#
#    def test_evaluates_expression_with_current_node_near_double_escaped_string_delimiter(self):
#        result = jp.evaluate({'\\2\\': 1, '~':2},
#                             [jp.PChild(targets=[jp.PExpression(code='"\\\\"+str(len(@))+"\\\\"')])] )
#        self.assertEqual([(1, '$["\\\\2\\\\"]')], result)

    # filters

    def test_evaluates_filter_child_for_dict(self):
        result = jp.evaluate({"a":1, "b":2, "c":3},
                             [jp.PChild(targets=[jp.PFilter(code='True')])] )
        self.assertEqual([(1, '$["a"]'), (2, '$["b"]'), (3, '$["c"]')], result)

    def test_evaluates_filter_child_for_sequence(self):
        result = jp.evaluate(["a","b","c"],
                             [jp.PChild(targets=[jp.PFilter(code='True')])] )
        self.assertEqual([("a", '$[0]'), ("b", '$[1]'), ("c", '$[2]')], result)

    def test_evaluates_operators_in_filter(self):
        result = jp.evaluate(["a","b","c"],
                             [jp.PChild(targets=[jp.PFilter(code='1>0 or 0>1')])] )
        self.assertEqual([("a", '$[0]'), ("b", '$[1]'), ("c", '$[2]')], result)

    def test_evaluates_current_node_in_filter(self):
        result = jp.evaluate(["foo","bar","baz"],
                             [jp.PChild(targets=[jp.PFilter(code='"a" in @')])] )
        self.assertEqual([("bar", '$[1]'), ("baz", '$[2]')], result)

    def test_evaluates_non_boolean_result_for_filter(self):
        result = jp.evaluate([1,6,4,3,8],
                             [jp.PChild(targets=[jp.PFilter(code='@ % 3')])] )
        self.assertEqual([(1, '$[0]'), (4, '$[2]'), (8, '$[4]')], result)

    def test_raises_error_for_bad_syntax_in_filter(self):
        with self.assertRaises(jp.PythonSyntaxError):
            jp.evaluate([1,2,3,4,5],
                        [jp.PChild(targets=[jp.PExpression(code='^!*&~')])] )
                        
    def test_evaluates_filter_with_builtins(self):
        result = jp.evaluate([1,2,3],
                             [jp.PChild(targets=[jp.PFilter(code='len("foo") > 2')])] )
        self.assertEqual([(1, '$[0]'), (2, '$[1]'), (3, '$[2]')], result)

    def test_evaluates_root_node_in_filter(self):
        result = jp.evaluate({"a":2, "b":3, "c":1},
                             [jp.PChild(targets=[jp.PFilter(code='@ >= $["a"]')])] )
        self.assertEqual([(2, '$["a"]'), (3, '$["b"]')], result)
    
    # failed steps
    
    def test_ignores_missing_property(self):
        result = jp.evaluate([{'b':1},{'a':2},{'a':3,'b':4}],
                             [jp.PChild(targets=[jp.PWildcard()]),
                              jp.PChild(targets=[jp.PProperty(name='b')])] )
        self.assertEqual([(1, '$[0]["b"]'), (4, '$[2]["b"]')], result)
        
    def test_ignores_missing_index(self):
        result = jp.evaluate({'a':['i','ii'], 'b':['iv','v','vi'], 'c':['vii','viii','ix']},
                             [jp.PChild(targets=[jp.PWildcard()]),
                              jp.PChild(targets=[jp.PSlice(index=2)])] )
        self.assertEqual([('vi', '$["b"][2]'), ('ix', '$["c"][2]')], result)

    def test_ignores_property_on_non_dict(self):
        result = jp.evaluate([1,'a',{'b':4},[2,3]],
                             [jp.PChild(targets=[jp.PWildcard()]),
                              jp.PChild(targets=[jp.PProperty(name='b')])] )
        self.assertEqual([(4, '$[2]["b"]')], result)

    def test_ignores_index_on_non_sequence(self):
        result = jp.evaluate([1,'a',{'b':4},[2,3]],
                             [jp.PChild(targets=[jp.PWildcard()]),
                              jp.PChild(targets=[jp.PSlice(index=1)])] )
        self.assertEqual([(3, '$[3][1]')], result)

    def test_applies_partial_slice_to_short_sequence(self):
        result = jp.evaluate(['a','b','c','d'],
                             [jp.PChild(targets=[jp.PSlice(start=1, end=10)])] )
        self.assertEqual([('b', '$[1]'), ('c', '$[2]'), ('d', '$[3]')], result)
        
    def test_ignores_non_syntax_error_in_expression(self):
        result = jp.evaluate(['a','b','c'],
                             [jp.PChild(targets=[jp.PExpression(code='len("a") > foo')])] )
        self.assertEqual([], result)

    def test_ignores_non_syntax_error_in_filter(self):
        result = jp.evaluate(['ay','bee','eff'],
                             [jp.PChild(targets=[jp.PFilter(code='@[2] == "e"')])] )
        self.assertEqual([('bee', '$[1]')], result)

    # spec examples

    def test_example_book_store_authors(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PChild(targets=[jp.PProperty(name='store')]),
                              jp.PChild(targets=[jp.PProperty(name='book')]),
                              jp.PChild(targets=[jp.PWildcard()]),
                              jp.PChild(targets=[jp.PProperty(name='author')])] )
        self.assertEqual([('Nigel Rees', '$["store"]["book"][0]["author"]'), 
                          ('Evelyn Waugh', '$["store"]["book"][1]["author"]'), 
                          ('Herman Melville', '$["store"]["book"][2]["author"]'), 
                          ('J. R. R. Tolkien', '$["store"]["book"][3]["author"]')], result)

    def test_example_all_authors(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PRecursive(targets=[jp.PProperty(name='author')])] )
        self.assertEqual([('Nigel Rees', '$["store"]["book"][0]["author"]'), 
                          ('Evelyn Waugh', '$["store"]["book"][1]["author"]'), 
                          ('Herman Melville', '$["store"]["book"][2]["author"]'), 
                          ('J. R. R. Tolkien', '$["store"]["book"][3]["author"]')], result)

    def test_example_all_things_in_store(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PChild(targets=[jp.PProperty(name='store')]),
                              jp.PChild(targets=[jp.PWildcard()])] )
        self.assertEqual([
                (
                    [
                        {
                            "category": "reference",
                            "author": "Nigel Rees",
                            "title": "Sayings of the Century",
                            "price": 8.95,
                        },
                        {
                            "category": "fiction",
                            "author": "Evelyn Waugh",
                            "title": "Sword of Honour",
                            "price": 12.99,
                        },
                        {
                            "category": "fiction",
                            "author": "Herman Melville",
                            "title": "Moby Dick",
                            "isbn": "0-553-21311-3",
                            "price": 8.99,
                        },
                        {
                            "category": "fiction",
                            "author": "J. R. R. Tolkien",
                            "title": "The Lord of the Rings",
                            "isbn": "0-395-19395-8",
                            "price": 22.99,
                        },
                    ],
                    '$["store"]["book"]'
                ),
                (
                    {
                        "color": "red",
                        "price": 19.95,
                    },
                    '$["store"]["bicycle"]'
                )
            ], result)

    def test_example_all_store_prices(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PChild(targets=[jp.PProperty(name='store')]),
                              jp.PRecursive(targets=[jp.PProperty(name='price')])] )
        self.assertEqual([(19.95, '$["store"]["bicycle"]["price"]'),
                          (8.95, '$["store"]["book"][0]["price"]'),
                          (12.99, '$["store"]["book"][1]["price"]'),
                          (8.99, '$["store"]["book"][2]["price"]'),
                          (22.99, '$["store"]["book"][3]["price"]')], result)

    def test_example_third_book(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PRecursive(targets=[jp.PProperty(name='book')]),
                              jp.PChild(targets=[jp.PSlice(index=2)])] )
        self.assertEqual([({
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            }, 
            '$["store"]["book"][2]')], result)

    def test_example_last_book(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PRecursive(targets=[jp.PProperty(name='book')]),
                              jp.PChild(targets=[jp.PSlice(start=-1)])] )
        self.assertEqual([({
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            }, 
            '$["store"]["book"][3]')], result)

    def test_example_first_two_books(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PRecursive(targets=[jp.PProperty(name='book')]),
                              jp.PChild(targets=[jp.PSlice(end=2)])] )
        self.assertEqual([({
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            }, 
            '$["store"]["book"][0]'),
            ({
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
            '$["store"]["book"][1]')], result)

    def test_example_books_with_isbn(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PRecursive(targets=[jp.PProperty(name='book')]),
                              jp.PChild(targets=[jp.PFilter(code='"isbn" in @')])] )
        self.assertEqual([({
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            }, 
            '$["store"]["book"][2]'), 
            ({
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            }, 
            '$["store"]["book"][3]')], result)

    def test_example_books_cheaper_than_ten(self):
        result = jp.evaluate(self.example,
                             [jp.PChild(targets=[jp.PRoot()]),
                              jp.PRecursive(targets=[jp.PProperty(name='book')]),
                              jp.PChild(targets=[jp.PFilter(code='@["price"] < 10')])] )
        self.assertEqual([({
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            }, 
            '$["store"]["book"][0]'),
            ({
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
            '$["store"]["book"][2]')], result)


class TestJsonPath(unittest.TestCase):

    def test_returns_values_by_default(self):
        result = jp.jsonpath({"a":1, "b":2, "c":"d"}, '$[*]')
        self.assertEqual([1, 2, "d"], result)

    def test_returns_values_if_specified(self):
        result = jp.jsonpath({"a":1, "b":2, "c":"d"}, '$[*]', jp.RESULT_TYPE_VALUE)
        self.assertEqual([1, 2, "d"], result)

    def test_returns_paths_if_specified(self):
        result = jp.jsonpath({"a":1, "b":2, "c":"d"}, '$[*]', jp.RESULT_TYPE_PATH)
        self.assertEqual(['$["a"]', '$["b"]', '$["c"]'], result)

    def test_returns_both_if_specified(self):
        result = jp.jsonpath({"a":1, "b":2, "c":"d"}, '$[*]', jp.RESULT_TYPE_BOTH)
        self.assertEqual([(1, '$["a"]'), (2, '$["b"]'), ("d", '$["c"]')], result)

    def test_returns_false_on_no_match(self):
        result = jp.jsonpath({"a":1, "b":2, "c":"d"}, '$.e')
        self.assertEqual(False, result)

    def test_returns_empty_list_on_no_match_if_specified(self):
        result = jp.jsonpath({"a":1, "b":2, "c":"d"}, '$.e', always_return_list=True)
        self.assertEqual([], result)

